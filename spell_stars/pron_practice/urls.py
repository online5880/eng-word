from django.urls import path
from . import views

urlpatterns = [
    # 발음 연습 페이지
    path('', views.pronunciation_practice_view, name='pron_practice'),
    
    # 음성 파일 업로드 (발음 평가)
    path('evaluate_pronunciation/', views.evaluate_pronunciation, name='evaluate_pronunciation'),
]
