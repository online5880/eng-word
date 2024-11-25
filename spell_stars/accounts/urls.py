from django.urls import path, include
from .views import (
    UserLoginView, SignupView, UserLogoutView, profileView, end_learning_session, student_learning_history
)


urlpatterns = [
    # 일반 뷰
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', profileView, name='profile'),

    # 학습 종료 엔드포인트
    path('end-learning/', end_learning_session, name='end_learning'),
    path('student/<int:student_id>/history/', student_learning_history, name='student_learning_history'),
]
