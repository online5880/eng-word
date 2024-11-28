from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import TestResult, TestResultDetail
from vocab_mode.models import Word
from sent_mode.models import Sentence
from accounts.models import Student
import os
import re
from django.db.models import Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import TestResultSerializer
from accounts.views import start_learning_session
import warnings
import random
import librosa

warnings.filterwarnings("ignore", category=FutureWarning)

model = apps.get_app_config('spell_stars').whisper_model
processor = apps.get_app_config('spell_stars').whisper_processor

TOTAL_QUESTIONS = 5
MAX_SCORE = 5
POINTS_PER_QUESTION = MAX_SCORE / TOTAL_QUESTIONS


def calculate_score(correct_answers, total_questions=TOTAL_QUESTIONS, max_score=MAX_SCORE):
    score = correct_answers * (max_score / total_questions)
    return round(score, 2)


def replace_word_with_blank(sentence, target_word):
    # 'The U.S.A.'는 하드코딩 처리
    if "The U.S.A." in sentence:
        sentence = sentence.replace("The U.S.A.", "_____")
    
    # 나머지 동사 변화형 처리
    escaped_word = re.escape(target_word)
    pattern = r'(?<!\w)' + escaped_word + r'(ing|ed|d|s|es)?(?!\w)'
    
    return re.sub(pattern, lambda match: '_____{}'.format(match.group(1) or ''), sentence)


def test_mode_view(request):
    print("test_mode_view called")

    # 단어 선택 동적으로 처리
    word_id = Word.objects.values_list("id", flat=True).order_by("?").first()

    if word_id:
        sentences = []
        sentence = Sentence.objects.filter(word_id=word_id).order_by("?").first()
        word = Word.objects.get(id=word_id)
        request.session["problem_solved"] = 1
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
        start_learning_session(request, learning_mode=3)

        return render(
            request,
            "test_mode/test_page.html",
            {
                "sentence": current_question["sentence"],
                "word": current_question["word"],
                "sentence_meaning": current_question["sentence_meaning"],
                "MEDIA_URL": settings.MEDIA_URL,
                "problem_solved": request.session["problem_solved"],
            },
        )
    else:
        return JsonResponse(
            {"error": "No words available in the database."}, status=404
        )


def clean_text(text):
    """특수문자를 제거하고 소문자로 변환, 공백 기준으로 단어를 리스트로 분리"""
    text = re.sub(r"[^\w\s]", "", text).lower()  # 특수문자 제거
    return text.split()  # 단어를 공백 기준으로 분리하여 리스트로 반환


# @csrf_exempt: 개발 중에만 사용, 실제 배포 시에는 CSRF 보호 필요
@csrf_exempt
def submit_audio(request):
    print("submit_audio called")

    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        print("오디오 파일", audio_file)

        # 사용자 인증 확인
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        try:
            user_id = request.user.id
            word = request.POST.get("word")
            if not word:
                return JsonResponse(
                    {"status": "error", "message": "Word is required"}, status=400
                )

            # 안전한 파일 이름 생성
            file_name = re.sub(r"[^a-zA-Z0-9._-]", "_", f"{word}_student.wav")

            # 저장 경로 설정
            save_dir = os.path.join(settings.MEDIA_ROOT, f"test_mode/user_{user_id}")
            os.makedirs(save_dir, exist_ok=True)

            # 파일 전체 경로
            file_path = os.path.join(save_dir, file_name)

            # 기존 파일 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 파일 저장
            relative_save_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            saved_path = default_storage.save(relative_save_path, ContentFile(audio_file.read()))
            print(f"File successfully saved at: {saved_path}")

            # Whisper 모델로 음성 텍스트 변환
            absolute_file_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            if not os.path.exists(absolute_file_path):
                return JsonResponse({"error": "File not found after saving"}, status=500)

            audio, rate = librosa.load(absolute_file_path, sr=16000)  # Whisper는 16kHz 필요
            inputs = processor(audio, sampling_rate=rate, return_tensors="pt")

            # 언어 설정: 특정 언어로 지정하려면 아래처럼 설정
            forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")

            # 모델 추론
            generated_ids = model.generate(
                inputs["input_features"], 
                forced_decoder_ids=forced_decoder_ids  # 언어 및 작업 설정 반영
            )

            # 결과 변환
            transcript = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            print(f"Transcript from Whisper: {transcript}")

            # 정답 단어와 비교
            clean_transcript = clean_text(transcript)  # 단어 리스트로 변환
            clean_target_word = clean_text(word)  # 정답 단어도 리스트로 변환
            is_correct = all(target_word in clean_transcript for target_word in clean_target_word)

            score_message = "정답입니다!" if is_correct else f"틀렸습니다. 정답은 '{word}'입니다."

            # 세션에 답 저장
            if "answers" not in request.session:
                request.session["answers"] = []
            request.session["answers"].append({
                "word_id": Word.objects.get(word=word).id,  # ID 저장
                "word": word,
                "transcript": transcript,
                "is_correct": is_correct,
            })

            # 성공 응답 반환
            return JsonResponse({
                "status": "success",
                "file_path": absolute_file_path,
                "is_correct": is_correct,
                "score_message": score_message,
                "message": "음성 파일이 성공적으로 저장되고 발음 평가가 완료되었습니다.",
            })

        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
            return JsonResponse({"error": f"Failed to transcribe audio: {str(e)}"}, status=500)

    return JsonResponse({"error": "No audio file received"}, status=400)    


def next_question(request):
    print("next_question called")
    
    request.session["problem_solved"] = request.session.get("problem_solved", 1) + 1

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
    sentence_with_blank = replace_word_with_blank(sentence.sentence, next_word.word)

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
            "problem_solved": request.session["problem_solved"],
        }
    )


def save_all_test_results(request):
    try:
        user_id = request.user.id
        student = Student.objects.get(user__id=user_id)
        answers = request.session.get("answers", [])

        # 동일한 단어에 대해 정답이 한 번이라도 나왔는지 확인
        word_correct_status = {}  # {word_id: is_correct}
        for answer in answers:
            word_id = answer["word_id"]
            if word_id not in word_correct_status:
                word_correct_status[word_id] = answer["is_correct"]
            else:
                # 이전 값이 False라도 새로운 값이 True면 True로 갱신
                word_correct_status[word_id] = word_correct_status[word_id] or answer["is_correct"]

        # 정답으로 처리된 단어 개수 계산
        correct_answers = sum(1 for is_correct in word_correct_status.values() if is_correct)
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
                is_correct=word_correct_status[word_id],  # 단어별 최종 정답 여부 저장
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
        request.session.pop("problem_solved", None)


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


class TestResultPagination(PageNumberPagination):
    page_size = 10

class TestResultListAPIView(APIView):
    """
    학생의 시험 결과 목록 제공 (페이지네이션 포함)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 현재 사용자 기준으로 학생 정보 가져오기
        student = request.user.student_profile  # user와 연결된 student profile 가져오기
        queryset = TestResult.objects.filter(student=student).order_by('-test_date')
        
        paginator = TestResultPagination()
        results_page = paginator.paginate_queryset(queryset, request)
        
        # Serializer를 사용하여 쿼리셋 데이터를 직렬화
        serializer = TestResultSerializer(results_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TestResultDetailAPIView(APIView):
    """
    특정 시험 결과의 세부 정보 제공
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        # 현재 사용자 기준으로 학생 정보 가져오기
        student = request.user.student_profile  # user와 연결된 student profile 가져오기
        
        try:
            # 특정 시험 결과를 해당 학생의 시험 결과로 필터링
            test_result = TestResult.objects.get(id=test_id, student=student)
        except TestResult.DoesNotExist:
            return Response({"error": "Test result not found"}, status=404)

        # 시험 결과 직렬화
        serializer = TestResultSerializer(test_result)
        return Response(serializer.data)