from django.urls import path, include
from .views import (
    UserLoginView, signup, UserLogoutView, profileView,
    StudentLearningLogViewSet, end_learning_session, StudentLogViewSet
)
from rest_framework.routers import DefaultRouter

# RESTful API 라우터 정의
router = DefaultRouter()
router.register(r'students/(?P<student_pk>\d+)/logs', StudentLogViewSet, basename='student-logs')
router.register(r'students/(?P<student_pk>\d+)/learning-logs', StudentLearningLogViewSet, basename='student-learning-logs')

urlpatterns = [
    # 일반 뷰
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),
    path('profile/', profileView, name='profile'),

    # 학습 종료 엔드포인트
    path('end-learning/', end_learning_session, name='end_learning'),
]
