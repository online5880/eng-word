import parselmouth
import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf
import os



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
    return trimmed_file_path, len(y) / sr, len(y_trimmed) / sr  # 원래와 트림된 오디오 길이 반환

# Function to extract formant frequencies
def extract_formants(file_path):
    try:
        snd = parselmouth.Sound(file_path)
        formant = snd.to_formant_burg()
        times = formant.ts()  # Time axis

        # Extract F1 and F2, handling None values as 0
        f1 = [
            formant.get_value_at_time(1, t) or 0
            for t in times
        ]
        f2 = [
            formant.get_value_at_time(2, t) or 0
            for t in times
        ]

        return times, f1, f2
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return [], [], []

# Function to plot overlapping formants
def plot_formants(times_native, f1_native, f2_native, times_student, f1_student, f2_student, save_path=None):
    plt.figure(figsize=(12, 6))

    # Plot F1
    plt.subplot(2, 1, 1)
    plt.plot(times_native, f1_native, label="Native F1", color="blue", linestyle="-")
    plt.plot(times_student, f1_student, label="Student F1", color="orange", linestyle="--")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Formant 1 (F1) Comparison")
    plt.legend()

    # Plot F2
    plt.subplot(2, 1, 2)
    plt.plot(times_native, f2_native, label="Native F2", color="blue", linestyle="-")
    plt.plot(times_student, f2_student, label="Student F2", color="orange", linestyle="--")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Formant 2 (F2) Comparison")
    plt.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Formant plot saved to {save_path}")
    else:
        plt.show()

# Function to plot overlapping waveforms
def plot_waveforms(native_audio_path, student_audio_path, save_path=None):
    try:
        snd_native = parselmouth.Sound(native_audio_path)
        native_waveform = snd_native.values[0]
        native_times = snd_native.xs()
        
        snd_student = parselmouth.Sound(student_audio_path)
        student_waveform = snd_student.values[0]
        student_times = snd_student.xs()
        
        plt.figure(figsize=(12, 6))

        # Overlapping waveforms
        plt.plot(native_times, native_waveform, label="Native Speaker", color="blue", alpha=0.7)
        plt.plot(student_times, student_waveform, label="Student Speaker", color="orange", alpha=0.7, linestyle="--")
        plt.title("Waveform Comparison")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend()

        if save_path:
            plt.savefig(save_path)
            print(f"Waveform plot saved to {save_path}")
        else:
            plt.show()
            
    except Exception as e:
        print(f"Error loading audio files: {e}")
