from django.urls import path
from . import views

urlpatterns = [
    # 발음 연습 페이지
    path('', views.pronunciation_practice_view, name='pron_practice'),
    
    # 음성 파일 업로드 (발음 평가)
    path('evaluate_pronunciation/', views.evaluate_pronunciation, name='evaluate_pronunciation'),
    
    # 다음 단어
    path('next_word/', views.next_word, name='next_word'),
    
    path('upload_audio/', views.upload_audio, name='upload_audio'),
]
