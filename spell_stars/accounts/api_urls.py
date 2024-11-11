from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListAPIView.as_view(), name='user-list'),  # 예: 사용자 리스트 API
]
