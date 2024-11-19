import plotly.graph_objects as go
import librosa
import numpy as np
# from PC_Pipeline.Parselscore import get_formants

def visualize_waveforms(native_path, student_path):
    """
    원어민과 학생의 발음 파형(Waveform)을 비교 시각화 + 애니메이션 추가.
    """
    # 원어민 음성 데이터 로드
    y_native, sr_native = librosa.load(native_path, sr=None)
    times_native = np.linspace(0, len(y_native) / sr_native, num=len(y_native))

    # 학생 음성 데이터 로드
    y_student, sr_student = librosa.load(student_path, sr=None)
    times_student = np.linspace(0, len(y_student) / sr_student, num=len(y_student))

    # 샘플링 간격 (애니메이션 속도 조정)
    step = 500  # 500 샘플씩 표시
    frames = []

    # Plotly 그래프 생성
    fig = go.Figure()

    # 기본 그래프 (빈 프레임)
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines',
        name='Native Waveform',
        line=dict(color='blue', width=2),
    ))
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines',
        name='Student Waveform',
        line=dict(color='red', width=2, dash='dash'),
    ))

    # 애니메이션 프레임 생성
    for i in range(0, len(times_native), step):
        frames.append(go.Frame(
            data=[
                go.Scatter(x=times_native[:i], y=y_native[:i], mode='lines', line=dict(color='blue', width=2)),
                go.Scatter(x=times_student[:i], y=y_student[:i], mode='lines', line=dict(color='red', width=2, dash='dash')),
            ],
            name=f"Frame {i}",
        ))

    # 프레임 설정
    fig.frames = frames

    # 레이아웃 설정
    fig.update_layout(
    title="Waveform Comparison (Animated)",
    xaxis=dict(
        title="Time (s)",
        showgrid=True
    ),
    yaxis=dict(
        title="Amplitude",
        showgrid=True
    ),
    legend=dict(
        title="Legend",
        x=0.8,
        y=1.1
    ),
    template="plotly_white",
    height=600,
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="Play",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(duration=50, redraw=True),
                            fromcurrent=True
                        )
                    ]
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0, redraw=False)
                        )
                    ]
                )
            ]
        )
    ]
)


    return fig