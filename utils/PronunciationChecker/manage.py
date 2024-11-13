import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "Pipeline"))

from PC_Pipeline.Visualization import extract_formants, plot_formants, plot_waveforms
from PC_Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score

def process_audio_files(directory_path, expected_word):
    # 'native'와 'student'라는 키워드를 사용해 원어민 및 학생 오디오 파일 구분
    files = os.listdir(directory_path)
    native_files = [f for f in files if "native" in f]
    student_files = [f for f in files if "student" in f]

    results = []

    # 각 학생 파일에 대해 원어민 파일과 비교하여 점수 계산 및 시각화
    for native_file, student_file in zip(native_files, student_files):
        native_path = os.path.join(directory_path, native_file)
        student_path = os.path.join(directory_path, student_file)
        
        print(f"Processing Native: {native_file} | Student: {student_file}")

        # Formant와 Phoneme 점수 계산
        formant_score = calculate_formant_score(native_path, student_path)
        phoneme_score = calculate_phoneme_score(student_path, expected_word)

        # 종합 점수 계산
        overall_score = calculate_overall_score(formant_score, phoneme_score)

        # 포먼트 시각화를 위한 데이터 추출
        times_native, f1_native, f2_native = extract_formants(native_path)
        times_student, f1_student, f2_student = extract_formants(student_path)

        # 포먼트 시각화 - 파일로 저장
        formant_save_path = f"formant_comparison_{native_file}_{student_file}.png"
        plot_formants(times_native, f1_native, f2_native, times_student, f1_student, f2_student, save_path=formant_save_path)

        # 파형 시각화 - 파일로 저장
        waveform_save_path = f"waveform_comparison_{native_file}_{student_file}.png"
        plot_waveforms(native_path, student_path, save_path=waveform_save_path)

        # 결과 저장
        result = {
            "native_file": native_file,
            "student_file": student_file,
            "formant_score": formant_score,
            "phoneme_score": phoneme_score,
            "overall_score": overall_score,
            "formant_plot": formant_save_path,
            "waveform_plot": waveform_save_path
        }
        results.append(result)

        # 점수 및 파일 경로 정보 출력
        print(f"Formant Score: {formant_score:.2f}")
        print(f"Phoneme Score: {phoneme_score:.2f}")
        print(f"Overall Pronunciation Score: {overall_score:.2f}")
        print(f"Formant plot saved to {formant_save_path}")
        print(f"Waveform plot saved to {waveform_save_path}")
        print("-" * 40)

    return results

if __name__ == "__main__":
    # 오디오 파일이 있는 폴더 경로 및 예상 단어 설정
    directory_path = "C:/Users/user/Desktop/eng-word/utils/PronunciationChecker/test_data"
    expected_word = "eraser"

    # 전체 파이프라인 실행
    start_time = datetime.now()
    results = process_audio_files(directory_path, expected_word)
    end_time = datetime.now()

    print(end_time - start_time)
    
    # 결과를 파일에 저장하거나 다른 방식으로 활용할 수 있음
    with open("pronunciation_results.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")
