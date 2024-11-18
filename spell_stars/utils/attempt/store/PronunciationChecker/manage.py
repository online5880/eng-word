import sys
import os
from datetime import datetime
import librosa
import soundfile as sf
sys.path.append(os.path.join(os.path.dirname(__file__), "Pipeline"))

from PC_Pipeline.Visualization import extract_formants, plot_formants, plot_waveforms
from PC_Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score

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

def process_audio_files(native_directory, student_directory, expected_word):
    native_files = sorted([f for f in os.listdir(native_directory) if f.endswith('.wav')])
    student_files = sorted([f for f in os.listdir(student_directory) if f.endswith('.wav')])

    results = []

    for native_file, student_file in zip(native_files, student_files):
        native_path = os.path.join(native_directory, native_file)
        student_path = os.path.join(student_directory, student_file)
        
        print(f"Processing Native: {native_file} | Student: {student_file}")

        # 무음 제거 후 새로운 경로로 설정
        trimmed_native_path = trim_silence(native_path)
        trimmed_student_path = trim_silence(student_path)

        # 발음 점수 계산
        formant_score = calculate_formant_score(trimmed_native_path, trimmed_student_path)
        phoneme_score = calculate_phoneme_score(trimmed_student_path, expected_word)
        overall_score = calculate_overall_score(formant_score, phoneme_score)

        # 포먼트 추출 및 그래프 그리기
        times_native, f1_native, f2_native = extract_formants(trimmed_native_path)
        times_student, f1_student, f2_student = extract_formants(trimmed_student_path)

        formant_save_path = f"formant_comparison_{native_file}_{student_file}.png"
        plot_formants(times_native, f1_native, f2_native, times_student, f1_student, f2_student, save_path=formant_save_path)

        waveform_save_path = f"waveform_comparison_{native_file}_{student_file}.png"
        plot_waveforms(trimmed_native_path, trimmed_student_path, save_path=waveform_save_path)

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

        print(f"Formant Score: {formant_score:.2f}")
        print(f"Phoneme Score: {phoneme_score:.2f}")
        print(f"Overall Pronunciation Score: {overall_score:.2f}")
        print(f"Formant plot saved to {formant_save_path}")
        print(f"Waveform plot saved to {waveform_save_path}")
        print("-" * 40)

    return results

if __name__ == "__main__":
    native_directory = "C:/Users/user/Desktop/eng-word/utils/PronunciationChecker/test_data/native_data"
    student_directory = "C:/Users/user/Desktop/eng-word/utils/PronunciationChecker/test_data/student_data"
    expected_word = "project"

    start_time = datetime.now()
    results = process_audio_files(native_directory, student_directory, expected_word)
    end_time = datetime.now()

    print(end_time - start_time)
    
    with open("pronunciation_results.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")
