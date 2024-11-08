import random
from django.shortcuts import render
import os
from django.http import JsonResponse
import librosa
import librosa.display
import numpy as np
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
from difflib import SequenceMatcher


def pronunciation_practice_view(request):
    words = [
        "apple",
        "banana",
        "orange",
        "grape",
        "kiwi",
    ]  # 이후 데이터베이스 구축 완료 후 거기에서 받아올 수 있게 수정해야 함
    random_word = random.choice(words)
    context = {"word": random_word}
    return render(request, "practice.html", context)


def next_word(request):
    words = [
        "apple",
        "banana",
        "orange",
        "grape",
        "kiwi",
    ]  # 이후 데이터베이스 구축 완료 후 거기에서 받아올 수 있게 수정해야 함
    random_word = random.choice(words)
    context = {"word": random_word}
    return render(request, "practice.html", context)


def evaluate_pronunciation(request):
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        file_path = os.path.join("media", "audio", audio_file.name)
        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        transcription = transcribe_audio(file_path)
        target_word = request.POST.get("target_word", "")
        score, waveform_similarity, mfcc_similarity, feedback = compare_pronunciation(
            file_path, target_word
        )

        # 결과 반환
        return JsonResponse(
            {
                "score": score,
                "transcription": transcription,
                "waveform_similarity": waveform_similarity,
                "mfcc_similarity": mfcc_similarity,
                "feedback": feedback,
            }
        )

    return JsonResponse({"error": "No audio file uploaded"}, status=400)


def transcribe_audio(file_path):
    """Whisper 모델을 사용하여 음성 파일을 텍스트로 변환 (여기서는 예시로 텍스트 변환 없이 바로 반환)"""
    try:
        transcription = (
            "apple"  # 실제로는 STT 모델을 통해 변환된 텍스트를 받아야 합니다.
        )
        return transcription
    except Exception as e:
        return str(e)


def compare_pronunciation(audio_file_path, target_word):
    """발음 유사도 계산"""
    # 1. 음성 파일을 librosa로 로드하고, 파형과 MFCC를 비교합니다.
    student_audio, sr = librosa.load(audio_file_path, sr=16000)

    # 원어민 발음 (여기서는 'apple'을 예시로 사용)
    # 하나의 음성 파일을 가지고 오는 대신 제시된 단어에 맞는 기준 음성 파일로 로드할 수 있게 수정해야 함
    native_audio, _ = librosa.load("native_apple.wav", sr=16000)

    # 2. 파형 비교
    waveform_similarity = compare_waveform(student_audio, native_audio)

    # 3. MFCC 비교
    student_mfcc = extract_mfcc(student_audio)
    native_mfcc = extract_mfcc(native_audio)
    mfcc_similarity = compare_mfcc(student_mfcc, native_mfcc)

    # 4. 텍스트 비교
    transcription = transcribe_audio(audio_file_path)
    score, feedback = compare_text(transcription, target_word)

    return score, waveform_similarity, mfcc_similarity, feedback


def compare_waveform(student_audio, native_audio):
    """파형 비교"""
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))

    # 학생 발음 파형
    librosa.display.waveshow(student_audio, ax=axs[0])
    axs[0].set_title("Student Pronunciation")

    # 원어민 발음 파형
    librosa.display.waveshow(native_audio, ax=axs[1])
    axs[1].set_title("Native Pronunciation")

    plt.tight_layout()
    plt.show()

    # 파형 유사도 (코사인 유사도로 간단히 비교)
    student_waveform = np.mean(student_audio)
    native_waveform = np.mean(native_audio)
    return 1 - cosine(student_waveform, native_waveform)


def extract_mfcc(audio):
    """MFCC 특징 벡터 추출"""
    mfcc = librosa.feature.mfcc(audio, sr=16000)
    return np.mean(mfcc, axis=1)


def compare_mfcc(student_mfcc, native_mfcc):
    """MFCC 특징 벡터 비교 (코사인 유사도)"""
    return 1 - cosine(student_mfcc, native_mfcc)


def compare_text(transcription, target_word):
    """텍스트 비교 - 세분화된 비교 방식"""
    # transcription과 target_word 간의 유사도 계산
    similarity = SequenceMatcher(
        None, transcription.lower().strip(), target_word.lower().strip()
    ).ratio()

    # 유사도에 따라 점수 부여
    if similarity == 1.0:
        score = 100  # 완벽하게 일치
        feedback = "발음이 정확합니다!"
    elif similarity >= 0.8:
        score = 85  # 매우 유사
        feedback = "발음이 매우 유사합니다!"
    elif similarity >= 0.6:
        score = 70  # 유사
        feedback = "발음이 괜찮습니다!"
    elif similarity >= 0.4:
        score = 50  # 약간 유사
        feedback = "발음이 약간 다릅니다."
    else:
        score = 30  # 유사하지 않음
        feedback = "발음이 매우 다릅니다."

    return score, feedback
