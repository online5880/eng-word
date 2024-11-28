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
        graphs = create_dashboard_graphs(student)
        if graphs:
            # 자녀의 이름을 context에 포함
            context = {
                "student_name": student.user.name,
                "graphs":graphs,
        }
        else:
            context = {
                "student_name": student.user.name,
                "graphs":"자녀의 학습 데이터가 없습니다.",
            }
        
        
    else:
        raise PermissionDenied("접근 권한이 없습니다.")

    return render(request, template_name, context)


def create_dashboard_graphs(student):
    """그래프를 생성하는 함수"""
    # 각 그래프를 먼저 생성
    fig1 = plot_learning_mode_hours(student)
    fig2 = plot_test_scores(student)
    fig3 = plot_learning_results(student)
    if not fig1 or not fig2 or not fig3:
        return "데이터가 없습니다."
        
    
    # 서브플롯을 결합 (서브플롯의 레이아웃을 설정)
    final_fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("학습 모드별 학습 시간", "시험 점수 변화(5점 만점)", "예문 학습 결과"),
        specs=[[{'type': 'domain'}], [{'type': 'xy'}], [{'type': 'xy'}]],
        vertical_spacing=0.1  # 서브플롯 사이의 간격 조정
    )

    # 각 플롯의 traces를 개별적으로 추가하고 범례를 분리
    for trace in fig1['data']:
        trace.update(legendgroup='group1', showlegend=True)
        final_fig.add_trace(trace, row=1, col=1)

    for trace in fig2['data']:
        trace.update(legendgroup='group2', showlegend=True)
        final_fig.add_trace(trace, row=2, col=1)

    for trace in fig3['data']:
        trace.update(legendgroup='group3', showlegend=True)
        final_fig.add_trace(trace, row=3, col=1)

    # 서브플롯 전체에 대한 레이아웃 설정
    final_fig.update_layout(
        height=2000,
        width=1000,
        title_text="대시보드",
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold'),
        legend=dict(
            yanchor="top",
            y=1.02,  # 상단 여백 조정
            xanchor="left",
            x=0.95,
            bgcolor='rgba(255,255,255,0.5)',  # 범례 배경 투명
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        )
    )

    # x축 포맷 설정 (연-월-일 형식)
    final_fig.update_xaxes(
        tickformat='%Y-%m-%d',  # 연-월-일 형식
        showgrid=True, gridwidth=1, gridcolor='lightgray'  # x축 그리드 설정
    )

    # y축 범위 설정 (필요한 서브플롯에만 적용)
    final_fig.update_yaxes(range=[0, 6], row=2, col=1)

    # 최종적으로 HTML로 변환하여 반환
    return final_fig.to_html(full_html=False)
