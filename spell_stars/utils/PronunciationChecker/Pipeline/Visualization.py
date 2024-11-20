import plotly.graph_objects as go
import plotly.subplots as sp
import matplotlib.pyplot as plt
import librosa
import numpy as np
import mpld3
from scipy.ndimage import gaussian_filter1d
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use('Agg')  # GUI 창을 비활성화하는 백엔드

# Waveform 비교 함수
def visualize_waveforms(native_path, student_path, smoothing_sigma=10):
    """
    원어민과 학생의 발음 파형 비교를 독립적으로 시각화.
    """
    # 원어민 음성 데이터 로드
    y_native, sr_native = librosa.load(native_path, sr=None)
    times_native = np.linspace(0, len(y_native) / sr_native, num=len(y_native))

    # 학생 음성 데이터 로드
    y_student, sr_student = librosa.load(student_path, sr=None)
    times_student = np.linspace(0, len(y_student) / sr_student, num=len(y_student))

    # 데이터 스무딩 (가우시안 필터 적용)
    y_native_smoothed = gaussian_filter1d(y_native, sigma=smoothing_sigma)
    y_student_smoothed = gaussian_filter1d(y_student, sigma=smoothing_sigma)

    # 서브플롯 구성
    fig = sp.make_subplots(
        rows=2, cols=1,
        subplot_titles=("Native Waveform", "Student Waveform"),
        vertical_spacing=0.2
    )

    # 그래프 추가: 원어민
    fig.add_trace(go.Scatter(
        x=times_native,
        y=y_native_smoothed,
        mode='lines',
        fill='tozeroy',
        line=dict(shape='spline', color='rgba(0, 0, 255, 0.5)', width=2),
        fillcolor='rgba(0, 122, 255, 0.4)',
        name='Native'
    ), row=1, col=1)

    # 그래프 추가: 학생
    fig.add_trace(go.Scatter(
        x=times_student,
        y=y_student_smoothed,
        mode='lines',
        fill='tozeroy',
        line=dict(shape='spline', color='orange', width=2),
        fillcolor='rgba(255, 99, 132, 0.4)',
        name='Student'
    ), row=2, col=1)

    # 레이아웃 설정
    fig.update_layout(
        title="Waveform Comparison: Native vs Student",
        height=600,
        showlegend=False,
        template="plotly_white"
    )

    return fig
def plot_f1_f2_comparison_mpld3(timestamps, f1_native, f1_student, f2_native, f2_student,username=""):
    """
    F1, F2 데이터를 Matplotlib과 mpld3를 사용해 비교 시각화.
    - F1 그래프는 위쪽, F2 그래프는 아래쪽.
    """
    # Matplotlib을 사용해 두 개의 서브플롯 생성
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # 첫 번째 서브플롯 (F1 비교)
    axes[0].plot(timestamps, f1_native, label="선생님 F1", color="blue", linewidth=2)
    axes[0].plot(timestamps, f1_student, label=f"{username} F1", color="orange", linewidth=2)
    axes[0].set_title("F1 점수 비교", fontsize=14)
    axes[0].set_ylabel("Frequency (Hz)")
    axes[0].legend(loc="upper right")
    axes[0].grid(True)

    # 두 번째 서브플롯 (F2 비교)
    axes[1].plot(timestamps, f2_native, label="선생님 F2", color="blue", linewidth=2)
    axes[1].plot(timestamps, f2_student, label=f"{username} F2", color="orange", linewidth=2)
    axes[1].set_title("F2 점수 비교", fontsize=14)
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Frequency (Hz)")
    axes[1].legend(loc="upper right")
    axes[1].grid(True)

    # 레이아웃 조정
    fig.suptitle("student의 포먼트 점수", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # mpld3로 HTML 변환
    html_fig = mpld3.fig_to_html(fig)

    # 그래프를 닫아 메모리 누수를 방지
    plt.close(fig)

    return html_fig

