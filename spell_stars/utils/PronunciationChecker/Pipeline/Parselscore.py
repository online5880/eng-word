import parselmouth
from parselmouth.praat import call
import numpy as np
import librosa
import soundfile as sf
import os


# 포먼트 주파수 평균 추출 함수
def get_formants(file_path,sr):
    """
    주어진 오디오 파일에서 시간에 따른 F1, F2 데이터를 추출합니다.
    """

    # 무음 제거된 파일에서 포먼트 추출
    snd = parselmouth.Sound(file_path, sampling_frequency=sr)
    formant = snd.to_formant_burg()

    # 시간 축 추출
    times = formant.ts()  # formant.ts()는 실제 포먼트 계산에서 사용된 시간 축

    # F1, F2 값 추출
    f1 = [formant.get_value_at_time(1, t) for t in times]
    f2 = [formant.get_value_at_time(2, t) for t in times]

    # NaN 값을 0으로 변환
    f1 = np.nan_to_num(f1)
    f2 = np.nan_to_num(f2)

    return times, f1, f2

