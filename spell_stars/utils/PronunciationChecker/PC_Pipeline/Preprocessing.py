import librosa
import soundfile as sf
import numpy as np
import os

# 오디오의 시작 부분 무음 제거
def trim_silence(file_path):
    """
    오디오 파일에서 무음 구간을 제거합니다.
    """
    y, sr = librosa.load(file_path, sr=None)
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)  # 20dB 이하를 무음으로 간주하고 트림

    # 임시 폴더 생성 (없으면 생성)
    temp_dir = "temp_trimmed"
    os.makedirs(temp_dir, exist_ok=True)

    # 임시 파일 경로 설정
    trimmed_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    sf.write(trimmed_file_path, y_trimmed, sr)
    return trimmed_file_path

# RMS 기반 음성 크기 표준화
def standardize_audio(file_path):
    """
    RMS를 기반으로 음성 크기를 표준화합니다.
    """
    y, sr = librosa.load(file_path, sr=None)
    rms = np.sqrt(np.mean(y**2))  # RMS 계산
    target_rms = 0.1  # 목표 RMS 값

    if rms > 0:
        y = y * (target_rms / rms)

    # 임시 폴더 생성 (없으면 생성)
    temp_dir = "temp_standardized"
    os.makedirs(temp_dir, exist_ok=True)
    standardized_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    sf.write(standardized_file_path, y, sr)
    return standardized_file_path

# 무음 제거와 RMS 표준화를 결합한 함수
def trim_and_standardize(file_path):
    """
    무음 제거 후 RMS 기반 음성 크기 표준화를 수행합니다.
    """
    trimmed_file_path = trim_silence(file_path)  # 무음 제거 수행
    standardized_file_path = standardize_audio(trimmed_file_path)  # RMS 표준화 적용
    return standardized_file_path
