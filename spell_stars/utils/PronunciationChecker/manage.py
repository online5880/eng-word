import shutil
import sys
import os
from datetime import datetime
import librosa
import soundfile as sf
# from .PC_Pipeline.Visualization import extract_formants, plot_formants, plot_waveforms
from .PC_Pipeline.Score import calculate_formant_score, calculate_phoneme_score, calculate_overall_score

def cleanup_temp_dir(temp_dir):
    """주어진 임시 폴더를 삭제"""
    print(temp_dir)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Deleted temporary directory: {temp_dir}")
    else:
        print(f"Directory does not exist: {temp_dir}")

# 오디오의 시작 부분 무음 제거
def trim_silence(file_path, native=True):
    y, sr = librosa.load(file_path, sr=None)
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)  # 20dB 이하를 무음으로 간주하고 트림

    # 임시 폴더 생성 (없으면 생성)
    if native:
        temp_dir = "media/trimmed/temp_trimmed_n"
    else:
        temp_dir = "media/trimmed/temp_trimmed_s"
        
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    
    # 임시 파일 경로 설정
    trimmed_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    sf.write(trimmed_file_path, y_trimmed, sr)
    return trimmed_file_path

def process_audio_files(native_file, student_file, expected_word, student_id):
    try:
        # 파일 경로가 올바른지 확인
        if not (os.path.isfile(native_file) and os.path.isfile(student_file)):
            raise ValueError("One of the audio file paths is invalid")
        
        print(f"Processing Native: {native_file} | Student: {student_file}")

        # 무음 제거 후 새로운 경로로 설정
        print("학생 경로",student_file, student_id)
        trimmed_native_path = trim_silence(native_file,True)
        trimmed_student_path = trim_silence(student_file,False)

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
            "formant_score": float(formant_score),
            "phoneme_score": float(phoneme_score),
            "overall_score": float(overall_score),
            "formant_plot": formant_save_path,
            "waveform_plot": waveform_save_path
        }

        print(f"Formant Score: {formant_score:.2f}")
        print(f"Phoneme Score: {phoneme_score:.2f}")
        print(f"Overall Pronunciation Score: {overall_score:.2f}")
        print(f"Formant plot saved to {formant_save_path}")
        print(f"Waveform plot saved to {waveform_save_path}")
        print("-" * 40)
        
        cleanup_temp_dir("media/trimmed/temp_trimmed_n") # native trimmed temp file 삭제
        cleanup_temp_dir("media/audio_files/students") #  trim 전 학생 음성 데이터 삭제

        return {"status": "success", "result": result}

    except Exception as e:
        print("Error in process_audio_files:", str(e))
        return {"status": "error", "message": str(e)}
    
    return results