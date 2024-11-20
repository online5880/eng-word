import plotly.graph_objects as go
import plotly.subplots as sp
import librosa
import numpy as np
from scipy.ndimage import gaussian_filter1d
from plotly.subplots import make_subplots

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
def plot_f1_f2_comparison(timestamps, f1_native, f1_student, f2_native, f2_student):
    """
    F1, F2 데이터를 Plotly를 사용해 비교 시각화.
    - F1 그래프는 위쪽, F2 그래프는 아래쪽.
    """
    # F1 설명 텍스트
    f1_hovertext = "F1 점수: 소리의 '입 벌린 정도'<br>" \
                   "입을 크게 벌리면 F1 숫자가 커지고,<br>" \
                   "입을 조금만 벌리면 F1 숫자가 작아져요!"

    # F2 설명 텍스트
    f2_hovertext = "F2 점수: 혀의 '앞뒤 위치'<br>" \
                   "혀가 앞쪽에 있으면 F2 숫자가 커지고,<br>" \
                   "혀가 뒤쪽에 있으면 F2 숫자가 작아져요!"

    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=1,
        vertical_spacing=0.2
    )

    # F1 비교
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=f1_native,
        mode='lines',
        line=dict(color='blue', width=4),
        name="선생님 F1",
        hoverinfo="text",
        hovertext=f1_hovertext
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=f1_student,
        mode='lines',
        line=dict(color='orange', width=4),
        # 이름 추가
        name="Student F1",
        hoverinfo="text",
        hovertext=f1_hovertext
    ), row=1, col=1)

    # F2 비교
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=f2_native,
        mode='lines',
        line=dict(color='blue', width=4),
        name="선생님 F2",
        hoverinfo="text",
        hovertext=f2_hovertext
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=f2_student,
        mode='lines',
        line=dict(color='orange', width=4),
        # 이름 추가
        name="Student F2",
        hoverinfo="text",
        hovertext=f2_hovertext
    ), row=2, col=1)

    # 레이아웃 설정
    # 이름 추가
    fig.update_layout(
        title="student의 포먼트 점수",
        height=800,
        template="plotly_white",
        legend=dict(
        title="Legend",
        x=1,
        y=1,
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="black",
        borderwidth=1
    ),
        xaxis_title="Time (s)",
        showlegend=True,
        )
    

    # 축별 설정
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency (Hz)", row=1, col=1)
    fig.update_yaxes(title_text="Frequency (Hz)", row=2, col=1)

    # 그래프 출력
    fig.show()

