from .Parselscore import get_formants
from .vosk_ import evaluate_pronunciation

def calculate_formant_score(native_audio_path, student_audio_path):
    print("calculate_formant_score [native_audio_path] : ", native_audio_path)
    print("calculate_formant_score [student_audio_path] : ", student_audio_path)
    f1_native, f2_native = get_formants(native_audio_path)
    f1_student, f2_student = get_formants(student_audio_path)

    f1_diff = abs(f1_native - f1_student)
    f2_diff = abs(f2_native - f2_student)

    max_diff = 1000

    formant_score = max(0, 100 - ((f1_diff + f2_diff)/(2*max_diff))* 100)

    return formant_score

def calculate_phoneme_score(audio_path, expected_word):
    phoneme_score = evaluate_pronunciation(audio_path, expected_word)
    return phoneme_score

def calculate_overall_score(formant_score, phoneme_score):
    formant_weight = 0.4
    phoneme_weight = 0.6

    overall_score = formant_score * formant_weight + phoneme_score * phoneme_weight
    return overall_score