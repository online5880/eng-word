# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("vocab_mode/", views.display_vocabulary_book, name="vocab_mode"),  # 단어 학습 페이지
    path('upload_audio/', views.upload_audio, name='upload_audio'),
]
