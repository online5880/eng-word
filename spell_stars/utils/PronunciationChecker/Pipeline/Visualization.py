import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import librosa
import numpy as np
import matplotlib
from scipy.ndimage import gaussian_filter1d
matplotlib.use('Agg')  # GUI 창을 비활성화하는 백엔드

# Waveform 비교 함수
def visualize_waveforms(native_path, student_path, smoothing_sigma=10,username=""):
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
        subplot_titles=("선생님 Waveform", f"{username} Waveform"),
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
        name='선생님'
    ), row=1, col=1)

    # 그래프 추가: 학생
    fig.add_trace(go.Scatter(
        x=times_student,
        y=y_student_smoothed,
        mode='lines',
        fill='tozeroy',
        line=dict(shape='spline', color='orange', width=2),
        fillcolor='rgba(255, 99, 132, 0.4)',
        name=f'{username}'
    ), row=2, col=1)

    # 레이아웃 설정
    fig.update_layout(
        title=f"Waveform Comparison: 선생님 vs {username}",
        height=600,
        showlegend=False,
        template="plotly_white"
    )

    return fig

def plot_f1_f2_comparison_plotly(timestamps, f1_native, f1_student, f2_native, f2_student, username=""):
    """
    F1, F2 데이터를 Plotly를 사용해 비교 시각화.
    - F1 그래프는 위쪽, F2 그래프는 아래쪽.
    """
    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=["F1 점수 비교", "F2 점수 비교"],
        vertical_spacing=0.1
    )

    # F1 비교 그래프
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=f1_native,
            mode='lines',
            name="선생님 F1",
            line=dict(color="blue", width=2)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=f1_student,
            mode='lines',
            name=f"{username} F1",
            line=dict(color="orange", width=2)
        ),
        row=1, col=1
    )

    # F2 비교 그래프
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=f2_native,
            mode='lines',
            name="선생님 F2",
            line=dict(color="blue", width=2)
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=f2_student,
            mode='lines',
            name=f"{username} F2",
            line=dict(color="orange", width=2)
        ),
        row=2, col=1
    )

    # 레이아웃 설정
    fig.update_layout(
        title=f"{username}의 포먼트 점수",
        height=600,
        template="plotly_white",
        legend=dict(x=0.5, y=1.1, orientation="h"),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency (Hz)", row=1, col=1)
    fig.update_yaxes(title_text="Frequency (Hz)", row=2, col=1)

    return fig

