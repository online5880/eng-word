import sys
import os
from datetime import datetime
import librosa
import soundfile as sf
# from .PC_Pipeline.Visualization import extract_formants, plot_formants, plot_waveforms
from .PC_Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score

# 오디오의 시작 부분 무음 제거
def trim_silence(file_path):
    y, sr = librosa.load(file_path, sr=None)
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)  # 20dB 이하를 무음으로 간주하고 트림

    # 임시 폴더 생성 (없으면 생성)
    temp_dir = "temp_trimmed"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    
    # 임시 파일 경로 설정
    trimmed_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    sf.write(trimmed_file_path, y_trimmed, sr)
    return trimmed_file_path

def process_audio_files(native_file, student_file, expected_word):
    try:
        # 파일 경로가 올바른지 확인
        if not (os.path.isfile(native_file) and os.path.isfile(student_file)):
            raise ValueError("One of the audio file paths is invalid")
        
        print(f"Processing Native: {native_file} | Student: {student_file}")

        # 무음 제거 후 새로운 경로로 설정
        trimmed_native_path = trim_silence(native_file)
        trimmed_student_path = trim_silence(student_file)

        # 발음 점수 계산
        formant_score = calculate_formant_score(trimmed_native_path, trimmed_student_path)
        phoneme_score = calculate_phoneme_score(trimmed_student_path, expected_word)
        overall_score = calculate_overall_score(formant_score, phoneme_score)

        # 포먼트 추출 및 그래프 그리기
        # times_native, f1_native, f2_native = extract_formants(trimmed_native_path)
        # times_student, f1_student, f2_student = extract_formants(trimmed_student_path)

        # 그래프 저장 경로 설정
        formant_save_path = os.path.join("media", f"formant_comparison_{os.path.basename(native_file)}_{os.path.basename(student_file)}.png")
        # plot_formants(times_native, f1_native, f2_native, times_student, f1_student, f2_student, save_path=formant_save_path)

        waveform_save_path = os.path.join("media", f"waveform_comparison_{os.path.basename(native_file)}_{os.path.basename(student_file)}.png")
        # plot_waveforms(trimmed_native_path, trimmed_student_path, save_path=waveform_save_path)

        result = {
            "native_file": native_file,
            "student_file": student_file,
            "formant_score": formant_score,
            "phoneme_score": phoneme_score,
            "overall_score": overall_score,
            "formant_plot": formant_save_path,
            "waveform_plot": waveform_save_path
        }

        print(f"Formant Score: {formant_score:.2f}")
        print(f"Phoneme Score: {phoneme_score:.2f}")
        print(f"Overall Pronunciation Score: {overall_score:.2f}")
        print(f"Formant plot saved to {formant_save_path}")
        print(f"Waveform plot saved to {waveform_save_path}")
        print("-" * 40)

        return {"status": "success", "result": result}

    except Exception as e:
        print("Error in process_audio_files:", str(e))
        return {"status": "error", "message": str(e)}
    
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
