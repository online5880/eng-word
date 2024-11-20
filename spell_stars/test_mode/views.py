from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import TestResult, TestResultDetail
from vocab_mode.models import Word
from sent_mode.models import Sentence
from accounts.models import StudentInfo
import os
import re
from django.db.models import Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.core.files.base import ContentFile
from accounts.views import start_learning_session
import warnings
import random

warnings.filterwarnings("ignore", category=FutureWarning)

model = apps.get_app_config('spell_stars').whisper_model

TOTAL_QUESTIONS = 10
MAX_SCORE = 100
POINTS_PER_QUESTION = MAX_SCORE / TOTAL_QUESTIONS


def calculate_score(correct_answers, total_questions=TOTAL_QUESTIONS, max_score=MAX_SCORE):
    score = correct_answers * (max_score / total_questions)
    return round(score, 2)


def replace_word_with_blank(sentence, target_word):
    # 동사 변화형을 처리할 정규식 패턴
    pattern = r'\b' + re.escape(target_word) + r'(ing|ed|d|s|es)?\b'
    
    return re.sub(pattern, lambda match: '_____{}'.format(match.group(1) or ''), sentence)


def test_mode_view(request):
    print("test_mode_view called")

    # 단어 선택 동적으로 처리
    word_id = Word.objects.values_list("id", flat=True).order_by("?").first()

    if word_id:
        sentences = []
        sentence = Sentence.objects.filter(word_id=word_id).order_by("?").first()
        word = Word.objects.get(id=word_id)
        if sentence:
            # 기존의 sentence.replace를 replace_word_with_blank로 변경
            sentence_with_blank = replace_word_with_blank(sentence.sentence, word.word)
            sentences.append(
                {
                    "sentence": sentence_with_blank,
                    "word_id": word.id,
                    "word": word.word,
                    "sentence_meaning": sentence.sentence_meaning
                }
            )

        if not sentences:
            return JsonResponse(
                {"error": "No sentences found for the selected words."}, status=404
            )

        # TestResult 모델에서 가장 최근의 test_number를 가져옵니다.
        last_test_result = TestResult.objects.aggregate(Max('test_number'))
        last_test_number = last_test_result['test_number__max'] or 0

        # 새로운 시험 번호는 마지막 번호 + 1
        test_number = last_test_number + 1

        # 첫 번째 문제 세션에 저장
        request.session["questions"] = sentences
        request.session["current_question_index"] = 0
        request.session["test_number"] = test_number
        request.session["answers"] = []  # 답을 기록할 리스트 초기화

        # 첫 번째 문제 렌더링
        current_question = sentences[0]
        request.session["target_word"] = [current_question["word_id"]]  # target_word 설정

        # 학습 시작 로그 생성
        start_learning_session(request, learning_mode=1)

        return render(
            request,
            "test_mode/test_page.html",
            {
                "sentence": current_question["sentence"],
                "word": current_question["word"],
                "sentence_meaning": current_question["sentence_meaning"],
                "MEDIA_URL": settings.MEDIA_URL,
            },
        )
    else:
        return JsonResponse(
            {"error": "No words available in the database."}, status=404
        )


@csrf_exempt
def submit_audio(request):
    print("submit_audio called")

    if request.method == "POST" and request.FILES.get("audio"):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        try:
            user_id = request.user.id
            word = request.POST.get("word")
            if not word:
                return JsonResponse(
                    {"status": "error", "message": "Word is required"}, status=400
                )

            # 저장 경로 설정
            save_path = f"test_mode/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{word}_student.wav"
            file_path = os.path.join(settings.MEDIA_ROOT, save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_student_audio_path = default_storage.save(
                file_path, ContentFile(request.FILES["audio"].read())
            )
            
            print(file_path)

            # Whisper 모델로 음성 텍스트 변환
            result = model.transcribe(file_path, language="en")
            transcript = result["text"]
            print(f"Transcript from Whisper: {transcript}")

            # 정답 단어와 비교 (특수문자 제외)
            def clean_text(text):
                """특수문자를 제거하고 소문자로 변환"""
                return re.sub(r"[^\w\s]", "", text).lower()

            clean_transcript = clean_text(transcript)
            clean_target_word = clean_text(word)

            is_correct = clean_target_word in clean_transcript.split()

            if is_correct:
                score = "정답입니다!"
            else:
                score = f"틀렸습니다. 정답은 '{word}'입니다."

            # 답을 세션에 저장
            if "answers" not in request.session:
                request.session["answers"] = []

            request.session["answers"].append(
                {
                    "word_id": Word.objects.get(word=word).id,  # ID 저장
                    "word": word,
                    "transcript": transcript,
                    "is_correct": is_correct,
                }
            )

            # 성공 응답 반환
            return JsonResponse(
                {
                    "status": "success",
                    "file_path": full_student_audio_path,
                    "is_correct": is_correct,  # True/False 그대로 유지
                    "score_message": score,   # 친화적 메시지 추가
                    "message": "음성 파일이 성공적으로 저장되고 발음 평가가 완료되었습니다.",
                }
            )

        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
            return JsonResponse(
                {"error": f"Failed to transcribe audio: {str(e)}"}, status=500
            )

    return JsonResponse({"error": "No audio file received"}, status=400)


def next_question(request):
    print("next_question called")

    # 세션에서 이미 푼 단어의 인덱스를 가져옵니다.
    answered_words = request.session.get("target_word", [])

    # 이미 푼 단어를 제외하고 랜덤으로 하나 가져오기
    next_word = Word.objects.exclude(id__in=answered_words).order_by("?").first()

    if not next_word:
        # 모든 단어를 다 푼 경우 결과 저장
        save_all_test_results(request)
        return JsonResponse(
            {"success": False, "message": "All words have been answered."}
        )

    # 해당 단어를 answered_words에 추가
    answered_words.append(next_word.id)

    # 세션에 갱신된 answered_words 리스트 저장
    request.session["target_word"] = answered_words

    # 해당 단어의 예문을 불러옵니다.
    sentence = Sentence.objects.filter(word=next_word).first()
    sentence_with_blank = sentence.sentence.replace(next_word.word, "_____")

    # 문제 끝나면 결과 저장
    current_question_index = request.session.get("current_question_index", 0) + 1
    request.session["current_question_index"] = current_question_index

    # 마지막 문제인지 확인
    is_last_question = current_question_index >= (TOTAL_QUESTIONS-1)

    return JsonResponse(
        {
            "success": True,
            "word": next_word.word,
            "sentence": sentence_with_blank if sentence else "No sentence available.",
            "sentence_meaning": sentence.sentence_meaning if sentence else "No sentence meaning available.",
            "is_last_question": is_last_question,  # 마지막 문제 여부 추가
        }
    )


def save_all_test_results(request):
    try:
        user_id = request.user.id
        student = StudentInfo.objects.get(id=user_id)
        answers = request.session.get("answers", [])

        correct_answers = sum([1 for answer in answers if answer["is_correct"]])
        score = calculate_score(correct_answers)

        test_number = request.session.get("test_number", 1)
        test_date = timezone.now()

        # 시험 결과 저장
        test_result = TestResult.objects.create(
            student=student,
            test_number=test_number,
            test_date=test_date,
            accuracy_score=score,
        )

        # 단어별 상세 결과 저장
        for answer in answers:
            word_id = answer.get("word_id")
            word = Word.objects.get(id=word_id)

            # Sentence를 Word 기반으로 조회
            sentence_obj = Sentence.objects.filter(word=word).first()

            TestResultDetail.objects.create(
                test_result=test_result,
                word=word,
                sentence=sentence_obj.sentence if sentence_obj else "No sentence provided",
                sentence_meaning=sentence_obj.sentence_meaning if sentence_obj else "No meaning provided",
                is_correct=answer.get("is_correct"),
            )

        print(f"Test result and details saved: {test_result}")

        return test_result

    except Exception as e:
        print(f"Error saving test results: {e}")
        raise
    
    finally:
        # 저장 후 세션 초기화
        request.session.pop("answers", None)
        request.session.pop("test_number", None)
        request.session.pop("is_last_question", None)
        request.session.pop("current_question_index", None)


def results_view(request):
    try:
        # 결과 저장
        latest_result = save_all_test_results(request)

        if latest_result:
            # 시험 결과에 속한 세부 정보를 가져오기
            details = TestResultDetail.objects.filter(test_result=latest_result)
            
            return render(
                request, 
                'test_mode/results.html', 
                {'result': latest_result, 'details': details}
            )
        else:
            return render(request, 'test_mode/results.html', {'error': 'No results found.'})

    except TestResult.DoesNotExist:
        return render(request, 'test_mode/results.html', {'error': 'Test result not found.'})
