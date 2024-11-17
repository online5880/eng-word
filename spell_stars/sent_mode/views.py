import os
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from vocab_mode.models import Word
from accounts.models import StudentInfo
import warnings
from django.apps import apps
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Sentence, LearningResult

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = apps.get_app_config("spell_stars").whisper_model


# 예문 학습 페이지 렌더링
def example_sentence_learning(request):
    user = request.user
    # 세션에서 선택된 테마 가져오기
    selected_theme = request.session.get('selected_theme', None)

    if not selected_theme:
        # 만약 테마가 세션에 없다면 사전 학습 페이지로 리디렉션
        return redirect('vocab_learning')  # 사전 학습 페이지로 리디렉션

    # 선택한 테마에 해당하는 단어들 가져오기
    words_in_theme = Word.objects.filter(category=selected_theme)
    
    # 단어 중에서 랜덤으로 하나 선택
    random_word = random.choice(words_in_theme)

    # 해당 단어에 매칭되는 예문 가져오기
    sentences = Sentence.objects.filter(word=random_word).order_by("?")[:5]

    # 예문에 단어를 빈칸으로 대체
    blank_sentences = []
    for sentence in sentences:
        blank_sentence = sentence.sentence.replace(random_word.word, "_____")
        blank_sentences.append({
            "sentence": blank_sentence,
            "meaning": sentence.sentence_meaning,
            "word": random_word.word
        })

    context = {
        "sentences": blank_sentences,
        "random_word": random_word
    }

    return render(request, "sent_mode/sent_practice.html", context)


@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            user_id = request.user.id
            word = request.POST.get("word")

            if not word:
                return JsonResponse(
                    {"status": "error", "message": "Word is required"}, status=400
                )

            # 세션에서 테마 정보 가져오기
            selected_theme = request.session.get('selected_theme', None)

            if not selected_theme:
                return JsonResponse(
                    {"status": "error", "message": "Theme is required, please start vocabulary learning first."},
                    status=400
                )

            # 저장 경로 설정
            save_path = f"pron_pc/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(request.FILES["audio"].read())
            )

            # 절대 경로로 변환
            native_audio_path = os.path.join(
                settings.MEDIA_ROOT, "audio_files/native/", f"{word}.wav"
            )
            full_student_audio_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # 발음 비교 처리
            result = process_audio_files(
                native_audio_path, full_student_audio_path, word
            )

            if result["status"] == "error":
                return JsonResponse(result)

            # 발음 점수 저장
            pronunciation_score = result["result"]["overall_score"]
            accuracy_score = 100 if word in request.POST.get("answer", "") else 0  # 예시 답안 비교
            frequency_score = 10  # 예시로 고정 점수 사용

            # 결과 저장
            student = StudentInfo.objects.get(user_id=user_id)
            LearningResult.objects.create(
                word=Word.objects.get(word=word),
                student=student,
                learning_category=selected_theme,  # 테마 정보 저장
                learning_date=request.POST.get("date"),
                pronunciation_score=pronunciation_score,
                accuracy_score=accuracy_score,
                frequency_score=frequency_score,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "file_path": full_student_audio_path,
                    "score": round(pronunciation_score, 1),
                    "message": "음성 파일이 성공적으로 저장되고 발음 평가가 완료되었습니다.",
                }
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def exit_learning_mode(request):
    # 세션 초기화
    if 'selected_theme' in request.session:
        del request.session['selected_theme']

    # 메인 페이지로 리디렉션
    return redirect('home')  # 홈 페이지로 이동