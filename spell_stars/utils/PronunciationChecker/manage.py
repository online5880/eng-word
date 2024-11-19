import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "Pipeline"))

from PC_Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score
from PC_Pipeline.Preprocessing import trim_and_standardize  # 새로운 전처리 함수 임포트
from PC_Pipeline.Visualization import visualize_waveforms

def process_audio_files(native_directory, student_directory, expected_word):
    native_files = sorted([f for f in os.listdir(native_directory) if f.endswith('.wav')])
    student_files = sorted([f for f in os.listdir(student_directory) if f.endswith('.wav')])

    results = []

    for native_file, student_file in zip(native_files, student_files):
        native_path = os.path.join(native_directory, native_file)
        student_path = os.path.join(student_directory, student_file)
        
        print(f"Processing Native: {native_file} | Student: {student_file}")

        # 무음 제거와 RMS 표준화를 결합한 함수 호출
        standardized_native_path = trim_and_standardize(native_path)
        standardized_student_path = trim_and_standardize(student_path)

        # 발음 점수 계산
        formant_score = calculate_formant_score(standardized_native_path, standardized_student_path)
        phoneme_score = calculate_phoneme_score(standardized_student_path, expected_word)
        overall_score = calculate_overall_score(formant_score, phoneme_score)

        
        # 시각화 생성 (파형 비교용)
        fig = visualize_waveforms(standardized_native_path, standardized_student_path)
        fig.show()

        # 결과 저장
        result = {
            "native_file": native_file,
            "student_file": student_file,
            "formant_score": formant_score,
            "phoneme_score": phoneme_score,
            "overall_score": overall_score
        }
        results.append(result)


        print(f"Formant Score: {formant_score:.2f}")
        print(f"Phoneme Score: {phoneme_score:.2f}")
        print(f"Overall Pronunciation Score: {overall_score:.2f}")
        print("-" * 40)

    return results

if __name__ == "__main__":
    native_directory = "C:/Users/user/Desktop/eng-word/spell_stars/utils/PronunciationChecker/test_data/native_data"
    student_directory = "C:/Users/user/Desktop/eng-word/spell_stars/utils/PronunciationChecker/test_data/student_data"
    expected_word = "project"

    start_time = datetime.now()
    results = process_audio_files(native_directory, student_directory, expected_word)
    end_time = datetime.now()

    print(end_time - start_time)
    
    with open("pronunciation_results.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")
