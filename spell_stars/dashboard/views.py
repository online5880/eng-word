from accounts.models import Student
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .utils import plot_learning_mode_hours, plot_test_scores, plot_learning_results
from accounts.models import ParentStudentRelation, Parent
from plotly.subplots import make_subplots


@login_required
def dashboard_view(request, student_id=None):
    if request.user.role == 'student':
        # 학생: 본인 데이터 확인
        student = get_object_or_404(Student, user=request.user)
        template_name = 'dashboard/dashboard.html'
        context = {
            "graphs": create_dashboard_graphs(student),
        }
    elif request.user.role == 'parent':
        # 부모: 자녀 데이터 확인
        if not student_id:
            raise PermissionDenied("학생 ID가 제공되지 않았습니다.")
        
        # 부모는 Parent 모델로 연결된 User를 통해 확인
        parent = get_object_or_404(Parent, user=request.user)  # user가 Parent 객체로 연결
        relation = get_object_or_404(ParentStudentRelation, student_id=student_id, parent=parent)
        student = relation.student  # 해당 학생 정보를 가져옴
        template_name = 'dashboard/student_dashboard.html'
        
        # 자녀의 이름을 context에 포함
        context = {
            "student_name": student.user.name,
            "graphs": create_dashboard_graphs(student),
        }
    else:
        raise PermissionDenied("접근 권한이 없습니다.")

    return render(request, template_name, context)


def create_dashboard_graphs(student):
    """그래프를 생성하는 함수"""
    fig1 = plot_learning_mode_hours(student)
    fig2 = plot_test_scores(student)
    fig3 = plot_learning_results(student)

    # 서브플롯 설정
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("학습 모드별 학습 시간", "시험 점수 변화", "학습 결과"),
        specs=[[{'type': 'domain'}, {'type': 'xy'}, {'type': 'xy'}]]
    )
    for trace in fig1['data']:
        fig.add_trace(trace, row=1, col=1)
    for trace in fig2['data']:
        fig.add_trace(trace, row=1, col=2)
    for trace in fig3['data']:
        fig.add_trace(trace, row=1, col=3)

    fig.update_layout(
        height=800,
        width=1000,
        title_text="대시보드",
        title_x=0.5
    )

    return fig.to_html(full_html=False)