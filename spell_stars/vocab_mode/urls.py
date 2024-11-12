from django.urls import path
from . import views

urlpatterns = [
    path("", views.word_learning_view, name="word_learning"),  # 단어 학습 페이지
    # path('sent_pratice/', views.sent_mode_view, name='sent_mode'),  # 예문 학습 모드 페이지로의 전환
]
