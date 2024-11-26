from django.urls import path
from . import views

urlpatterns = [
    # 대시보드 URL
    # student_id는 부모에게만 필요한 파라미터로, 없으면 학생 본인의 대시보드가 열리도록
    path('dashboard/', views.dashboard_view, name='dashboard'),  
    path('dashboard/<int:student_id>/', views.dashboard_view, name='student_dashboard'),  # 부모용 대시보드
]
