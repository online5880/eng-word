from django.utils import timezone
from accounts.models import StudentLearningLog, Student
from test_mode.models import TestResult
from sent_mode.models import LearningResult
import math
import pandas as pd
import plotly.express as px


# 학습 모드 매핑
LEARNING_MODE_MAPPING = {
    1: '사전학습 + 예문학습',
    2: '시험',
    3: '발음 연습'
}

# 학습 모드별 학습 시간 그래프
def plot_learning_mode_hours(request):
    user_id = request.user.id
    student = Student.objects.get(user__id=user_id)
    logs = StudentLearningLog.objects.filter(student=student)
    if not logs:
        return ""
    # 학습 모드별 시간 계산
    data = []
    for log in logs:
        if log.start_time and log.end_time:
            total_time = (log.end_time - log.start_time).total_seconds() / 60
            total_time = math.ceil(total_time)  # 분 단위로 반올림
        else:
            total_time = 0  # start_time이나 end_time이 None이면 0분으로 처리
        learning_mode_name = LEARNING_MODE_MAPPING.get(log.learning_mode, '기타')
        data.append({'학습 모드': learning_mode_name, '학습 시간': total_time})
    
    df = pd.DataFrame(data)
    
    # 학습 모드별 총 학습 시간 합산
    df_grouped = df.groupby('학습 모드')['학습 시간'].sum().reset_index()
    
    # 파이차트 생성
    fig = px.pie(
        df_grouped, 
        names='학습 모드', 
        values='학습 시간', 
        title='학습 모드별 총 학습 시간',
        color='학습 모드',  # 학습 모드별 색상
        color_discrete_map={
            "사전학습 + 예문학습": "#1f77b4", 
            "시험": "#ff7f0e", 
            "발음 연습": "#2ca02c",
        },
        hole=0.3  # 도넛 모양 (optional)
    )
    fig.update_traces(textinfo='percent+label')
    
    return fig


# 시험 점수 변화 그래프
def plot_test_scores(request):
    user_id = request.user.id
    student = Student.objects.get(user__id=user_id)
    test_results = TestResult.objects.filter(student=student).order_by('test_date')
    if not test_results:
        return ""
    data = pd.DataFrame({
        '시험 날짜': [result.test_date for result in test_results],
        '시험 점수': [result.accuracy_score for result in test_results],
    })

    fig = px.line(
        data,
        x='시험 날짜',
        y='시험 점수',
        title='시험 점수 변화(5점 만점)',
        markers=True,
        color_discrete_sequence=["#9b59b6"]  # 색상 변경
    )
    fig.update_traces(name='시험 점수')
    
    return fig


def plot_learning_results(request):
    user_id = request.user.id
    student = Student.objects.get(user__id=user_id)
    results = LearningResult.objects.filter(student=student).order_by('learning_date').defer('word_id') 
    if not results:
        return ""
    data = pd.DataFrame({
        '예문 학습 날짜': [result.learning_date for result in results],
        '발음 점수': [result.pronunciation_score for result in results],
        '총점(정오답)': [result.accuracy_score for result in results],
    })

    fig = px.line(
        data,
        x='예문 학습 날짜',
        y=['발음 점수', '총점(정오답)'],
        title='예문 학습 결과',
        markers=True,
        color_discrete_sequence=["#1f77b4", "#ff7f0e"]  # 색상 변경
    )

    return fig
