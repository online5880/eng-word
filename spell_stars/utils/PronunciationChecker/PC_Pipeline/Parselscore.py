import parselmouth
from parselmouth.praat import call
import numpy as np

# 포먼트 주파수 평균 추출 함수
def get_formants(file_path):
    snd = parselmouth.Sound(file_path)
    formant = snd.to_formant_burg()
    f1 = []
    f2 = []
    for t in formant.ts():
        f1.append(formant.get_value_at_time(1, t))
        f2.append(formant.get_value_at_time(2, t))
    return np.nanmean(f1), np.nanmean(f2)  # 평균 값 반환, NaN 값 무시