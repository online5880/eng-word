from .Parselscore import get_formants
from .vosk_ import evaluate_pronunciation
import numpy as np
import math
def calculate_formant_score(native_f1, native_f2, student_f1, student_f2):
    """
    시간에 따른 F1, F2 데이터를 기반으로 포먼트 점수를 계산합니다.
    """
    # F1, F2 차이 계산
    f1_diff = np.abs(native_f1 - student_f1)
    f2_diff = np.abs(native_f2 - student_f2)

    # 최대 차이값 설정
    max_diff = 1000  # 포먼트 값의 허용 범위

    # F1, F2 평균 차이를 점수로 변환
    avg_diff = (f1_diff + f2_diff) / 2
    formant_score = np.clip(100 - (avg_diff / max_diff) * 100, 0, 100)

    return np.mean(formant_score)  # 평균 점수 반환


def calculate_phoneme_score(audio_path, expected_word):
    phoneme_score = evaluate_pronunciation(audio_path, expected_word)
    return phoneme_score

def normalize_score(score, min_score, max_score):
    """
    정규화 함수
    """
    return (score - min_score) / (max_score - min_score) * 100 if max_score != min_score else 100

def calculate_overall_score(formant_score, phoneme_score):
    # 각 지표별 특성에 맞게 최대, 최소 값 선정
    min_formant_score, max_formant_score = 40, 95
    min_phoneme_score, max_phoneme_score = 0, 100

    # 점수 정규화
    normalized_formant_score = normalize_score(formant_score, min_formant_score, max_formant_score)
    normalized_phoneme_score = normalize_score(phoneme_score, min_phoneme_score, max_phoneme_score)

    # 가중치 설정
    formant_weight = 0.4
    phoneme_weight = 0.6

    # 최종 점수 계산
    overall_score = (normalized_formant_score * formant_weight) + (normalized_phoneme_score * phoneme_weight)
    overall_score = clamp(overall_score,0.,100.)
    return overall_score

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))