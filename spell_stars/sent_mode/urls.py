from django.urls import path
from . import views

urlpatterns = [
    path("", views.example_sentence_learning, name="example_sentence_learning"),
    path("upload_audio/", views.upload_audio, name="upload_audio"), 
    path("result/", views.sent_result, name="sent_result"), # 반드시 포함
    path('sent/practice/', views.sent_practice, name='sent_practice'),
]
