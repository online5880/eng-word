# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # 대시보드 메인 화면
    path('plot/learning_mode/', views.plot_learning_mode_hours, name='plot_learning_mode_hours'),
    path('plot/test_scores/', views.plot_test_scores, name='plot_test_scores'),
    path('plot/learning_results/', views.plot_learning_results, name='plot_learning_results'),
    path('plot/total_learning_time/', views.plot_total_learning_time, name='plot_total_learning_time'),
]
