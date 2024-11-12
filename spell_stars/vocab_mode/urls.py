# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("vocab_mode/<int:book_id>/", views.display_vocabulary_book, name="vocab_mode"),  # 단어 학습 페이지
    path('sent_practice/', views.sent_mode_view, name='sent_mode'),  # 예문 학습 모드 페이지로의 전환
]
