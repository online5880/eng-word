import os
import librosa
import numpy as np
from scipy.spatial.distance import cosine
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Word
import random
import warnings
import whisper
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = whisper.load_model("small")


# 발음 연습 페이지를 렌더링하는 뷰
def pronunciation_practice_view(request):
    random_word = Word.objects.values('word', 'meanings').order_by("?").first()
    if random_word:
        return render(
            request, "pron_practice/pron_practice.html", {"word": random_word['word']}
        )
    else:
        return JsonResponse({"error": "No words available in the database."}, status=404)



@csrf_exempt
def evaluate_pronunciation(request):
    try:
        if request.method == "POST" and request.FILES.get("audio_file"):
            user_id = request.user.id
            random_word = Word.objects.order_by("?").first()
            if not random_word:
                return JsonResponse({"error": "No words available in the database."}, status=404)

            target_word = random_word.word_text

            # 저장 경로 설정
            save_path = f'audio_files/students/user_{user_id}/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            file_name = f"{target_word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(file_path, ContentFile(request.FILES['audio_file'].read()))

            # 원어민 발음 파일 경로 설정
            native_file_path = os.path.join(settings.MEDIA_ROOT, "audio_files", "native", f"{target_word}.wav")

            if not os.path.exists(native_file_path):
                return JsonResponse({"error": f"Native audio file for {target_word} not found."}, status=404)

            # 발음 비교 수행
            result = process_audio_files(native_file_path, full_path, target_word)

            return JsonResponse({
                "status": "success",
                "score": result['score'],
                "feedback": result['feedback'],
                "target_word": target_word,
            })

        return JsonResponse({"error": "No audio file uploaded"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


# 다음 단어로 이동하는 뷰
def next_word(request):
    random_word = Word.objects.order_by("?").first()
    if random_word:
        return JsonResponse({"next_word": random_word.word_text})
    else:
        return JsonResponse({"error": "No words available in the database."}, status=404)
