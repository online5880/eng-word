from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import StudentLearningLog
from test_mode.models import TestResult
from sent_mode.models import LearningResult
import matplotlib.pyplot as plt
import koreanize_matplotlib
from io import BytesIO
import seaborn as sns

import pandas as pd
from datetime import timedelta

# 대시보드 기본 페이지
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


# 학습 모드 매핑
LEARNING_MODE_MAPPING = {
    0: '사전학습 + 예문학습',
    1: '시험',
    2: '발음 연습'
}

# 학습 모드별 학습 시간 계산
def learning_mode_hours(student):
    logs = StudentLearningLog.objects.filter(student=student)
    mode_hours = []
    
    for log in logs:
        total_time = log.end_time - log.start_time if log.end_time else timedelta(0)
        learning_mode_name = LEARNING_MODE_MAPPING.get(log.learning_mode, '기타')
        mode_hours.append({
            'learning_mode': learning_mode_name,
            'total_time': total_time
        })
    
    return mode_hours


# 학습 모드별 학습 시간 그래프
def plot_learning_mode_hours(request):
    student = request.user
    mode_hours = learning_mode_hours(student)
    
    # 데이터프레임으로 변환
    data = pd.DataFrame(mode_hours)
    data['total_time'] = data['total_time'].dt.total_seconds() / 3600  # 시간 단위로 변환

    # 독립적인 Figure 객체 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='learning_mode', y='total_time', data=data, palette='viridis', ax=ax)
    ax.set_xlabel('학습 모드')
    ax.set_ylabel('학습 시간 (시간)')
    ax.set_title('학습 모드별 학습 시간 비율')
    plt.xticks(rotation=45)
    fig.tight_layout()

    response = HttpResponse(content_type='image/png')
    fig.savefig(response, format="png", dpi=300)
    plt.close(fig)  # Figure 닫기
    return response


# 학생별 시험 점수 추이 구하기
def get_test_scores(student):
    # 학생별로 시험 결과를 가져와서 정확도 점수 추이 구하기
    test_results = TestResult.objects.filter(student=student).order_by('test_date')
    return [(test.test_date, test.accuracy_score) for test in test_results]


# 시험 점수 변화 그래프
def plot_test_scores(request):
    student = request.user
    test_results = TestResult.objects.filter(student=student).order_by('test_date')
    data = pd.DataFrame({
        'dates': [result.test_date for result in test_results],
        'scores': [result.accuracy_score for result in test_results],
    })

    # 독립적인 Figure 객체 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='dates', y='scores', data=data, marker='o', ax=ax)
    ax.set_xlabel('시험 날짜')
    ax.set_ylabel('정확도 점수')
    ax.set_title('시험 점수 변화')
    fig.tight_layout()

    response = HttpResponse(content_type='image/png')
    fig.savefig(response, format="png", dpi=300)
    plt.close(fig)
    return response


# 학습 결과 그래프
def plot_learning_results(request):
    student_id = request.user.id
    results = LearningResult.objects.filter(student_id=student_id).order_by('learning_date')
    
    data = pd.DataFrame({
        'dates': [result.learning_date for result in results],
        'pronunciation_scores': [result.pronunciation_score for result in results],
        'accuracy_scores': [result.accuracy_score for result in results],
    })

    # 독립적인 Figure 객체 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='dates', y='pronunciation_scores', data=data, label='발음 점수', marker='o', ax=ax)
    sns.lineplot(x='dates', y='accuracy_scores', data=data, label='정확도 점수', marker='x', ax=ax)
    ax.set_xlabel('학습 날짜')
    ax.set_ylabel('점수')
    ax.set_title('학습 결과 (발음 점수 vs 정확도 점수)')
    ax.legend()
    fig.tight_layout()

    response = HttpResponse(content_type='image/png')
    fig.savefig(response, format="png", dpi=300)
    plt.close(fig)
    return response


# 전체 학습 시간 그래프
def plot_total_learning_time(request):
    student = request.user
    logs = StudentLearningLog.objects.filter(student=student)
    total_time = sum([(log.end_time - log.start_time).total_seconds() for log in logs if log.end_time]) / 3600

    labels = ['학습 시간', '기타 시간']
    sizes = [total_time, max(0, 24 - total_time)]
    
    # 독립적인 Figure 객체 생성
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'))
    ax.set_title('전체 학습 시간')

    response = HttpResponse(content_type='image/png')
    fig.savefig(response, format="png", dpi=300)
    plt.close(fig)
    return response