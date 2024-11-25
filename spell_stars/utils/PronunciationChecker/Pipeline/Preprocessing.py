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
def standardize_audio(file_path, output_audio_file_path:str):
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
    sf.write(standardized_file_path, y, sr,format="wav")
        # 지정된 경로에 저장
    if not output_audio_file_path.endswith(".wav"):  # 확장자 확인 및 추가
        output_audio_file_path += ".wav"
    sf.write(output_audio_file_path, y, sr, format="WAV")  # 파일 포맷 명시
    return standardized_file_path

# 무음 제거와 RMS 표준화를 결합한 함수
def trim_and_standardize(file_path:str,output_audio_file_path="") ->tuple[str,str]:
    """
    무음 제거 후 RMS 기반 음성 크기 표준화를 수행합니다.
    """
    trimmed_file_path = trim_silence(file_path)  # 무음 제거 수행
    standardized_file_path = standardize_audio(trimmed_file_path,output_audio_file_path)  # RMS 표준화 적용
    print("trim_and_standardize 후 학생 음성 파일 저장 완료",output_audio_file_path)
    return trimmed_file_path, standardized_file_path


# Cross-Correlation 기반 발음 동기화 함수

def align_start_point(native_path, student_path, target_sr=16000):
    """
    Cross-Correlation을 기반으로 원어민과 학생 신호의 발음 시작점을 동기화.
    """
    # 원어민 오디오 로드 및 리샘플링
    y_native, sr_native = librosa.load(native_path, sr=None)
    if sr_native != target_sr:
        y_native = librosa.resample(y_native, orig_sr=sr_native, target_sr=target_sr)
        sr_native = target_sr

    # 학생 오디오 로드 및 리샘플링
    y_student, sr_student = librosa.load(student_path, sr=None)
    if sr_student != target_sr:
        y_student = librosa.resample(y_student, orig_sr=sr_student, target_sr=target_sr)
        sr_student = target_sr

    # Cross-Correlation 수행
    correlation = np.correlate(y_native, y_student, mode="full")
    lag = np.argmax(correlation) - len(y_student) + 1

    # 학생 신호의 시작점 조정
    if lag > 0:
        y_student_aligned = np.pad(y_student, (lag, 0), mode="constant")[:len(y_native)]
        y_native_aligned = y_native
    elif lag < 0:
        y_native_aligned = np.pad(y_native, (-lag, 0), mode="constant")[:len(y_student)]
        y_student_aligned = y_student
    else:
        y_native_aligned = y_native
        y_student_aligned = y_student

    return y_native_aligned, y_student_aligned, target_sr
