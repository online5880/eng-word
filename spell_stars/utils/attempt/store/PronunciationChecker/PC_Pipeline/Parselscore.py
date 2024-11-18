import parselmouth
from parselmouth.praat import call
import numpy as np
import librosa
import soundfile as sf
import os

# 오디오의 시작 부분 무음 제거
def trim_silence(file_path):
    y, sr = librosa.load(file_path, sr=None)
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)  # 20dB 이하를 무음으로 간주하고 트림
    
    # 임시 폴더 생성 (없으면 생성)
    temp_dir = "temp_trimmed"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 임시 파일 경로 설정
    trimmed_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    sf.write(trimmed_file_path, y_trimmed, sr)
    return trimmed_file_path

# 포먼트 주파수 평균 추출 함수
def get_formants(file_path):
    # 파일을 무음 제거 후 새로운 경로로 설정
    trimmed_file_path = trim_silence(file_path)
    
    # 무음 제거된 파일로 포먼트 추출
    snd = parselmouth.Sound(trimmed_file_path)
    formant = snd.to_formant_burg()
    f1 = []
    f2 = []
    for t in formant.ts():
        f1.append(formant.get_value_at_time(1, t))
        f2.append(formant.get_value_at_time(2, t))
    return np.nanmean(f1), np.nanmean(f2)  # 평균 값 반환, NaN 값 무시
