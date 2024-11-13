import parselmouth
import matplotlib.pyplot as plt
import numpy as np

# 포먼트 주파수 추출 함수
def extract_formants(file_path):
    try:
        snd = parselmouth.Sound(file_path)
        formant = snd.to_formant_burg()
        times = formant.ts()  # 시간 축

        # F1, F2 포먼트 추출, None 값은 0으로 처리
        f1 = [
            (
                formant.get_value_at_time(1, t)
                if formant.get_value_at_time(1, t) is not None
                else 0
            )
            for t in times
        ]
        f2 = [
            (
                formant.get_value_at_time(2, t)
                if formant.get_value_at_time(2, t) is not None
                else 0
            )
            for t in times
        ]

        return times, f1, f2
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return [], [], []

# 포먼트 시각화 함수
def plot_formants(times_native, f1_native, f2_native, times_student, f1_student, f2_student, save_path=None):
    plt.figure(figsize=(12, 6))

    # F1 시각화
    plt.subplot(2, 1, 1)
    if len(times_native) > 0 and len(f1_native) > 0:
        plt.plot(times_native, f1_native, label="Native F1", color="blue")
    if len(times_student) > 0 and len(f1_student) > 0:
        plt.plot(
            times_student, f1_student, label="Student F1", color="orange", linestyle="--"
        )
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Formant 1 (F1) Comparison")
    plt.legend()

    # F2 시각화
    plt.subplot(2, 1, 2)
    if len(times_native) > 0 and len(f2_native) > 0:
        plt.plot(times_native, f2_native, label="Native F2", color="blue")
    if len(times_student) > 0 and len(f2_student) > 0:
        plt.plot(
            times_student, f2_student, label="Student F2", color="orange", linestyle="--"
        )
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Formant 2 (F2) Comparison")
    plt.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)  # 이미지로 저장
        print(f"Formant plot saved to {save_path}")
    else:
        plt.show()  # 화면에 표시

# 파형 시각화 함수
def plot_waveforms(native_audio_path, student_audio_path, save_path=None):
    try:
        # 원어민 오디오 로드
        snd_native = parselmouth.Sound(native_audio_path)
        native_waveform = snd_native.values[0]
        native_times = snd_native.xs()
        
        # 학생 오디오 로드
        snd_student = parselmouth.Sound(student_audio_path)
        student_waveform = snd_student.values[0]
        student_times = snd_student.xs()
        
        plt.figure(figsize=(12, 8))

        # 원어민 파형
        plt.subplot(2, 1, 1)
        plt.plot(native_times, native_waveform, color='blue')
        plt.title("Native Speaker Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")

        # 학생 파형
        plt.subplot(2, 1, 2)
        plt.plot(student_times, student_waveform, color='orange')
        plt.title("Student Speaker Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)  # 이미지로 저장
            print(f"Waveform plot saved to {save_path}")
        else:
            plt.show()  # 화면에 표시
            
    except Exception as e:
        print(f"Error loading audio files: {e}")
