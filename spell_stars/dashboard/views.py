import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import StudentLearningLog
from test_mode.models import TestResult
from sent_mode.models import LearningResult
from datetime import timedelta
import math


# 학습 모드 매핑
LEARNING_MODE_MAPPING = {
    0: '사전학습 + 예문학습',
    1: '시험',
    2: '발음 연습'
}

# 대시보드 기본 페이지
def dashboard_view(request):
    fig1 = plot_learning_mode_hours(request)
    fig2 = plot_test_scores(request)
    fig3 = plot_learning_results(request)
    fig4 = plot_total_learning_time(request)
    
    # 서브플롯 생성 (2행 2열), pie 차트를 위한 domain 설정
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("학습 모드별 학습 시간", "전체 학습 시간", "시험 점수 변화", "학습 결과 (발음 점수 vs 정확도 점수)"),
        vertical_spacing=0.1,  # 서브플롯 간의 세로 간격
        horizontal_spacing=0.1,  # 서브플롯 간의 가로 간격
        specs=[[{'type': 'xy'}, {'type': 'domain'}],  # 첫 번째 행, 두 번째 서브플롯은 pie 차트 (domain)
               [{'type': 'xy'}, {'type': 'xy'}]]  # 두 번째 행은 모두 xy 차트
    )

    # fig1, fig4는 첫 번째 행에 배치
    for trace in fig1['data']:
        fig.add_trace(trace, row=1, col=1)
    
    for trace in fig4['data']:
        fig.add_trace(trace, row=1, col=2)

    # fig2, fig3는 두 번째 행에 배치
    for trace in fig2['data']:
        fig.add_trace(trace, row=2, col=1)
    
    for trace in fig3['data']:
        fig.add_trace(trace, row=2, col=2)

    # 레이아웃 설정
    fig.update_layout(
        height=800,  # 전체 높이
        width=1000,  # 전체 너비
        title_text="대시보드",
        showlegend=False,  # 범례 숨기기
        title_x=0.5,
        font=dict(family="Arial, sans-serif", size=16, color="black"),  # 글꼴 설정
        plot_bgcolor="#f9f9f9",  # 밝은 배경 색상 설정
        paper_bgcolor="#ffffff",  # 전체 배경 색상 설정 (흰색)
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold')  # 제목을 굵게 설정
    )

    # HTML로 변환하여 렌더링
    graph_html = fig.to_html(full_html=False)
    context = {
        "graphs": graph_html
    }
    return render(request, 'dashboard/dashboard.html', context)


# 학습 모드별 학습 시간 그래프
def plot_learning_mode_hours(request):
    student = request.user
    logs = StudentLearningLog.objects.filter(student=student)
    
    # 학습 모드별 시간 계산
    data = []
    for log in logs:
        if log.start_time and log.end_time:
            total_time = (log.end_time - log.start_time).total_seconds() / 3600
            total_time = math.ceil(total_time)  # 시간 단위로 반올림
        else:
            total_time = 0  # start_time이나 end_time이 None이면 0시간으로 처리
        learning_mode_name = LEARNING_MODE_MAPPING.get(log.learning_mode, '기타')
        data.append({'학습 모드': learning_mode_name, '학습 시간': total_time})
    
    df = pd.DataFrame(data)
    fig = px.bar(
        df, 
        x='학습 모드', 
        y='학습 시간',
        title='학습 모드별 학습 시간',
        color='학습 모드',
        text='학습 시간',
        color_discrete_map={"사전학습 + 예문학습": "#1f77b4", "시험": "#ff7f0e", "발음 연습": "#2ca02c"}  # 색상 지정
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=18, color="black"),  # 글씨체 및 크기 변경
        title_x=0.5,
        plot_bgcolor="#f9f9f9",  # 밝은 배경색 변경
        paper_bgcolor="#ffffff",  # 종이 배경색 변경
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold')  # 제목을 굵게 설정
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    return fig


# 시험 점수 변화 그래프
def plot_test_scores(request):
    student = request.user
    test_results = TestResult.objects.filter(student=student).order_by('test_date')

    data = pd.DataFrame({
        '시험 날짜': [result.test_date.strftime('%Y-%m-%d') for result in test_results],
        '정확도 점수': [result.accuracy_score for result in test_results],
    })

    fig = px.line(
        data,
        x='시험 날짜',
        y='정확도 점수',
        title='시험 점수 변화',
        markers=True,
        color_discrete_sequence=["#9b59b6"]  # 색상 변경
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold')  # 제목을 굵게 설정
    )

    return fig


# 학습 결과 그래프
def plot_learning_results(request):
    student = request.user
    results = LearningResult.objects.filter(student=student).order_by('learning_date')

    data = pd.DataFrame({
        '학습 날짜': [result.learning_date.strftime('%Y-%m-%d') for result in results],
        '발음 점수': [result.pronunciation_score for result in results],
        '정확도 점수': [result.accuracy_score for result in results],
    })

    fig = px.line(
        data,
        x='학습 날짜',
        y=['발음 점수', '정확도 점수'],
        title='학습 결과 (발음 점수 vs 정확도 점수)',
        markers=True,
        color_discrete_sequence=["#1f77b4", "#ff7f0e"]  # 색상 변경
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold')  # 제목을 굵게 설정
    )

    return fig


# 전체 학습 시간 그래프
def plot_total_learning_time(request):
    student = request.user
    logs = StudentLearningLog.objects.filter(student=student)

    total_time = sum(
        [(log.end_time - log.start_time).total_seconds() for log in logs if log.end_time]
    ) / 3600

    labels = ['학습 시간', '기타 시간']
    values = [total_time, max(0, 24 - total_time)]

    fig = px.pie(
        values=values,
        names=labels,
        title='전체 학습 시간',
        hole=0.3,
        color_discrete_sequence=["#56b4e9", "#f1d1f1"]  # 색상 변경
    )
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold')  # 제목을 굵게 설정
    )

    return fig
