from PC_Pipeline.Parselscore import get_formants
from PC_Pipeline.vosk_ import evaluate_pronunciation

def calculate_formant_score(native_audio_path, student_audio_path):
    f1_native, f2_native = get_formants(native_audio_path)
    f1_student, f2_student = get_formants(student_audio_path)

    f1_diff = abs(f1_native - f1_student)
    f2_diff = abs(f2_native - f2_student)

    max_diff = 1000

    formant_score = max(0, 100 - ((f1_diff + f2_diff) / (2 * max_diff)) * 100)

    return formant_score

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
    formant_weight = 0.3
    phoneme_weight = 0.7

    # 최종 점수 계산
    overall_score = (normalized_formant_score * formant_weight) + (normalized_phoneme_score * phoneme_weight)
    return overall_score