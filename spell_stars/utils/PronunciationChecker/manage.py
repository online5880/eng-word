import shutil
import sys
import os
from datetime import datetime
import numpy as np

from .Pipeline.Parselscore import get_formants
from .Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score
from .Pipeline.Preprocessing import trim_and_standardize, align_start_point
from .Pipeline.Visualization import visualize_waveforms, plot_f1_f2_comparison
sys.path.append("C:/Users/user/Desktop/eng-word/spell_stars/utils/PronunciationChecker/Pipeline")

def cleanup_temp_dir(temp_dir):
    """주어진 임시 폴더를 삭제"""
    print(temp_dir)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Deleted temporary directory: {temp_dir}")
    else:
        print(f"Directory does not exist: {temp_dir}")
        
def process_audio_files(native_directory, student_directory, expected_word, user_id):
    """
    원어민과 학생의 오디오 파일을 처리하고 점수 및 시각화를 생성.
    """
    native_files = sorted([f for f in os.listdir(native_directory) if f.endswith('.wav')])
    student_files = sorted([f for f in os.listdir(student_directory) if f.endswith('.wav')])

    # 결과 저장 리스트 초기화

    result = {}

    for native_file, student_file in zip(native_files, student_files):
        native_path = os.path.join(native_directory, native_file)
        student_path = os.path.join(student_directory, student_file)

        print(f"Processing Native: {native_file} | Student: {student_file}")

        try:
            # 무음 제거 및 RMS 표준화
            standardized_native_path = trim_and_standardize(native_path)
            standardized_student_path = trim_and_standardize(student_path)

            # Cross-Correlation 기반 동기화
            print("Aligning start points using Cross-Correlation...")
            y_native_aligned, y_student_aligned, sr = align_start_point(
                standardized_native_path, standardized_student_path
            )

            # 동기화된 신호를 사용하여 Formants 계산
            native_times, native_f1, native_f2 = get_formants(y_native_aligned, sr)
            student_times, student_f1, student_f2 = get_formants(y_student_aligned, sr)

            # NaN 값 체크
            if any(np.isnan(native_f1)) or any(np.isnan(native_f2)) or any(np.isnan(student_f1)) or any(np.isnan(student_f2)):
                print("Warning: NaN values detected in formant data. Skipping this pair.")
                continue

            # 시간 축 보간
            common_timestamps = np.linspace(0, min(native_times[-1], student_times[-1]), 500)
            native_f1_interp = np.interp(common_timestamps, native_times, native_f1)
            native_f2_interp = np.interp(common_timestamps, native_times, native_f2)
            student_f1_interp = np.interp(common_timestamps, student_times, student_f1)
            student_f2_interp = np.interp(common_timestamps, student_times, student_f2)

            # Formant 점수 계산
            formant_score = calculate_formant_score(
                native_f1=native_f1_interp,
                native_f2=native_f2_interp,
                student_f1=student_f1_interp,
                student_f2=student_f2_interp
            )
            # Formant 점수가 70점 미만인 경우 False 출력
            if formant_score < 70:
                print(f"Formant Score for {student_file}: {formant_score} (Below Threshold)")
                print("Result: False")
                continue

            # 음소 점수 계산
            phoneme_score = calculate_phoneme_score(standardized_student_path, expected_word)

            # 총 점수 계산
            overall_score = calculate_overall_score(formant_score, phoneme_score)

            # 1. 파형 비교 시각화
            waveform_fig = visualize_waveforms(standardized_native_path, standardized_student_path)

            # 2. Formant 비교 시각화
            plot_f1_f2_comparison(
                timestamps=common_timestamps,
                f1_native=native_f1_interp,
                f1_student=student_f1_interp,
                f2_native=native_f2_interp,
                f2_student=student_f2_interp
            )

            # 결과 저장
            result = {
                "native_file": native_file,
                "student_file": student_file,
                "formant_score": round(formant_score, 2),
                "phoneme_score": round(phoneme_score, 2),
                "overall_score": round(overall_score, 2),
                "waveform_fig" : waveform_fig
            }

            # 결과 출력
            print(f"Formant Score: {result['formant_score']}")
            print(f"Phoneme Score: {result['phoneme_score']}")
            print(f"Overall Pronunciation Score: {result['overall_score']}")
            print("-" * 40)

        except Exception as e:
            print(f"Error processing {native_file} and {student_file}: {e}")
            continue

    return result

if __name__ == "__main__":
    # 경로 설정
    native_directory = "C:/Users/user/Desktop/eng-word/spell_stars/utils/PronunciationChecker/test_data/native_data"
    student_directory = "C:/Users/user/Desktop/eng-word/spell_stars/utils/PronunciationChecker/test_data/student_data"
    expected_word = "project"

    start_time = datetime.now()

    # 메인 처리 함수 호출
    result = process_audio_files(native_directory, student_directory, expected_word)

    end_time = datetime.now()
    print(f"Total Processing Time: {end_time - start_time}")

