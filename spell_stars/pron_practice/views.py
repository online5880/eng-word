import random
from django.shortcuts import render
import os
from django.http import JsonResponse  # JsonResponse 임포트

# Whisper API 설정 (예시)
# openai.api_key = "YOUR_API_KEY"  # 실제 API 키를 사용하세요


def pronunciation_practice_view(request):
    # 단어 목록에서 랜덤 단어 선택 (모델 없이 단어 목록을 임시로 생성한 예시)
    words = ["apple", "banana", "orange", "grape", "kiwi"]  # 예시 단어 목록
    random_word = random.choice(words)

    context = {"word": random_word}

    return render(request, "practice.html", context)


def next_word(request):
    # 단어 변경 시 랜덤으로 새 단어 선택 (모델 없이 단어 목록을 임시로 생성한 예시)
    words = ["apple", "banana", "orange", "grape", "kiwi"]  # 예시 단어 목록
    random_word = random.choice(words)

    context = {"word": random_word}

    return render(request, "practice.html", context)


def evaluate_pronunciation(request):
    # POST로 받은 음성 파일 처리
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        # 서버에 음성 파일 저장
        file_path = os.path.join("media", "audio", audio_file.name)
        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # STT 모델을 사용하여 음성 파일을 텍스트로 변환 (Whisper 모델을 대체하는 예시)
        transcription = transcribe_audio(file_path)

        # 목표 단어와 비교하여 발음 유사도 점수 산출
        target_word = request.POST.get("target_word", "")  # 목표 단어를 받아옴
        score = compare_pronunciation(transcription, target_word)

        # 결과 반환
        return JsonResponse({"score": score, "transcription": transcription})

    return JsonResponse({"error": "No audio file uploaded"}, status=400)


def transcribe_audio(file_path):
    """Whisper 모델을 사용하여 음성 파일을 텍스트로 변환 (여기서는 예시로 텍스트 변환 없이 바로 반환)"""
    try:
        # Whisper API로 음성 파일을 텍스트로 변환하는 예시
        transcription = (
            "apple"  # 실제로는 STT 모델을 통해 변환된 텍스트를 받아야 합니다.
        )
        return transcription
    except Exception as e:
        return str(e)


def compare_pronunciation(transcription, target_word):
    """발음 유사도 계산"""
    score = 0

    # 텍스트 비교: 목표 단어와 변환된 텍스트가 일치하는지 확인
    if transcription.lower().strip() == target_word.lower().strip():
        score = 100
    else:
        # 발음 차이에 따른 점수 부여 (간단한 예시로, 실제로는 좀 더 정교하게 구현해야 할 수 있음)
        score = 50  # 예시로 고정값을 사용, 실제로는 유사도를 계산하여 점수 부여

    return score
