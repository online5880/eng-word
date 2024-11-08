from django.urls import path
from . import views

urlpatterns = [
    path("", views.test_mode_view, name="test_mode"),  # 기본 경로에 test_mode_view 연결
    path("recognize/<int:question_id>/", views.recognize_audio, name="recognize_audio"),
]
