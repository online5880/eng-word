from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListAPIView.as_view(), name='user-list'),  # 예: 전체 유저 조회
    path('users/<int:id>/',views.UserRetrieveAPIView.as_view(),name='user-detail'),
    path('register/',views.UserCreateAPIView.as_view(),name="user-register"), # 생성
]
