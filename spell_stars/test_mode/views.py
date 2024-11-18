from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import TestResult
from vocab_mode.models import Word
from sent_mode.models import Sentence
from accounts.models import StudentInfo
import os
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

TOTAL_QUESTIONS = 2
MAX_SCORE = 100
POINTS_PER_QUESTION = MAX_SCORE / TOTAL_QUESTIONS


def calculate_score(correct_answers, total_questions=TOTAL_QUESTIONS, max_score=MAX_SCORE):
    score = correct_answers * (max_score / total_questions)
    return round(score, 2)


def test_mode_view(request):
    print("test_mode_view called")

    # 단어 선택 동적으로 처리
    random_word_ids = Word.objects.values_list("id", flat=True).order_by("?")[:TOTAL_QUESTIONS]

    if random_word_ids:
        sentences = []
        for word_id in random_word_ids:
            sentence = Sentence.objects.filter(word_id=word_id).order_by("?").first()
            word = Word.objects.get(id=word_id)
            if sentence:
                sentence_with_blank = sentence.sentence.replace(word.word, "_____")
                sentences.append(
                    {
                        "sentence": sentence_with_blank,
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
        request.session["target_word"] = current_question["word"]  # target_word 설정

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
            full_path = default_storage.save(
                file_path, ContentFile(request.FILES["audio"].read())
            )
            
            print(file_path)

            # Whisper 모델로 음성 텍스트 변환
            result = model.transcribe(file_path, language="en")
            transcript = result["text"]
            print(f"Transcript from Whisper: {transcript}")

            # 예문에서 정답 단어와 비교하여 점수 계산
            target_word = word
            is_correct = target_word.lower() in transcript.lower()

            # 답을 세션에 저장
            question_index = request.session.get("current_question_index", 0)
            if "answers" not in request.session:
                request.session["answers"] = []

            request.session["answers"].append(
                {
                    "word": target_word,
                    "transcript": transcript,
                    "is_correct": is_correct,
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
    answered_words = request.session.get("answered_words", [])

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
    request.session["answered_words"] = answered_words

    # 해당 단어의 예문을 불러옵니다.
    sentence = Sentence.objects.filter(word=next_word).first()

    # 문제 수가 5번에 다다르면 결과 저장
    current_question_index = request.session.get("current_question_index", 0) + 1
    request.session["current_question_index"] = current_question_index

    if current_question_index == TOTAL_QUESTIONS:
        save_all_test_results(request)

    return JsonResponse(
        {
            "success": True,
            "word": next_word.word,
            "sentence": sentence.sentence if sentence else "No sentence available.",
            "sentence_meaning": sentence.sentence_meaning if sentence else "No sentence meaning available.",
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
        result = TestResult(
            student=student,
            test_number=test_number,
            test_date=test_date,
            accuracy_score=score,
            frequency_score=0,
        )
        result.save()

        print(f"Test result saved: {result}")
        
        return redirect("main")

    except StudentInfo.DoesNotExist:
        print(f"Student with id {user_id} does not exist.")
        raise
