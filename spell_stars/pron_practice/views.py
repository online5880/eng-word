import os
import whisper
import librosa
import numpy as np
from scipy.spatial.distance import cosine
from django.shortcuts import render
from django.http import JsonResponse
from difflib import SequenceMatcher
from django.conf import settings
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


# Whisper 모델 로드 (small 모델 사용)
model = whisper.load_model("small")

# 단어를 고정 (eraser만)
current_word = "eraser"

# 발음 연습 페이지를 렌더링하는 뷰
def pronunciation_practice_view(request):
    return render(request, "practice.html", {"word": current_word})

def evaluate_pronunciation(request):
    try:
        if request.method == "POST" and request.FILES.get("audio_file"):
            # 사용자 음성을 파일로 저장
            audio_file = request.FILES["audio_file"]

            # 업로드된 파일의 정보 확인
            file_name = audio_file.name
            file_size = audio_file.size
            file_type = audio_file.content_type

            print(f"Received file: {file_name}")
            print(f"File size: {file_size} bytes")
            print(f"File type: {file_type}")

            if file_size == 0:
                return JsonResponse({"error": "Uploaded file is empty. Please upload a valid audio file."}, status=400)

            # 확장자 강제로 .wav로 변경 (이름에 .wav가 포함되지 않는 경우에만)
            if not file_name.endswith(".wav"):
                file_name = file_name.split('.')[0] + ".wav"

            # 파일 저장 경로 설정
            user_file_path = os.path.join(settings.MEDIA_ROOT, "user", file_name)
            print(f"User file path: {user_file_path}")

            # 디렉토리 생성 및 파일 저장
            try:
                os.makedirs(os.path.dirname(user_file_path), exist_ok=True)  # 사용자 파일 디렉토리 생성
                with open(user_file_path, "wb") as f:
                    for chunk in audio_file.chunks():
                        f.write(chunk)
                print(f"File saved successfully at {user_file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
                return JsonResponse({"error": f"Failed to save file: {str(e)}"}, status=500)

            # 발음 비교 수행
            score, waveform_similarity, mfcc_similarity, feedback = compare_pronunciation(user_file_path, current_word)

            return JsonResponse(
                {
                    "score": score,
                    "feedback": feedback,
                    "waveform_similarity": waveform_similarity,
                    "mfcc_similarity": mfcc_similarity
                }
            )

        return JsonResponse({"error": "No audio file uploaded"}, status=400)
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

# 발음 비교 함수
def compare_pronunciation(user_file_path, target_word):
    # 사용자 음성 로드
    try:
        student_audio, sr = librosa.load(user_file_path, sr=16000)
    except Exception as e:
        return None, None, None, f"Error loading user audio file: {str(e)}"

    # 원어민 기준 음성 파일 로드
    native_file_path = os.path.join(
        settings.MEDIA_ROOT, "audio", "native", "eraser_a.wav"
    )
    try:
        native_audio, _ = librosa.load(native_file_path, sr=16000)
    except Exception as e:
        return None, None, None, f"Error loading native audio file: {str(e)}"

    # 파형 비교
    waveform_similarity = compare_waveform(student_audio, native_audio)

    # MFCC 비교
    student_mfcc = extract_mfcc(student_audio, sr)
    native_mfcc = extract_mfcc(native_audio, sr)
    mfcc_similarity = compare_mfcc(student_mfcc, native_mfcc)

    # 텍스트 비교
    transcription = transcribe_audio(user_file_path)
    score, feedback = compare_text(transcription, target_word)

    return score, waveform_similarity, mfcc_similarity, feedback

# 파형 비교 함수
def compare_waveform(student_audio, native_audio):
    # 평균을 통해 1차원 벡터로 변환
    student_waveform = np.mean(student_audio)
    native_waveform = np.mean(native_audio)
    return 1 - cosine([student_waveform], [native_waveform])

# MFCC 특징 벡터 추출
def extract_mfcc(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)  # MFCC 벡터 생성
    return np.mean(mfcc, axis=1)  # 각 차원의 평균값을 통해 1차원 벡터로 변환

# MFCC 비교 함수
def compare_mfcc(student_mfcc, native_mfcc):
    # 1차원 벡터로 비교 수행
    return 1 - cosine(student_mfcc, native_mfcc)

# 텍스트 비교 함수
def compare_text(transcription, target_word):
    similarity = SequenceMatcher(
        None, transcription.lower().strip(), target_word.lower().strip()
    ).ratio()

    if similarity == 1.0:
        score = 100
        feedback = "발음이 정확합니다!"
    elif similarity >= 0.8:
        score = 85
        feedback = "발음이 매우 유사합니다!"
    elif similarity >= 0.6:
        score = 70
        feedback = "발음이 괜찮습니다!"
    elif similarity >= 0.4:
        score = 50
        feedback = "발음이 약간 다릅니다."
    else:
        score = 30
        feedback = "발음이 매우 다릅니다."

    return score, feedback

# STT 모델을 통해 음성을 텍스트로 변환
def transcribe_audio(file_path):
    try:
        # Whisper 모델로 텍스트 변환
        result = model.transcribe(file_path)
        transcription = result["text"]
        print(f"Whisper Transcription Result: {transcription}")
        return transcription
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return f"Error during transcription: {str(e)}"

# 다음 단어로 이동하는 뷰 (단어가 하나라 계속 "eraser"로 유지)
def next_word(request):
    return JsonResponse({"next_word": current_word})