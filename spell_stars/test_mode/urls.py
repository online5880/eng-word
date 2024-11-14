from django.urls import path
from . import views

urlpatterns = [
    path("", views.test_mode_view, name="test_mode"),  # 시험 모드 페이지
    path(
        "recognize_audio/<int:question_id>/",
        views.recognize_audio,
        name="recognize_audio",
    ),
    path(
        "next_question/<int:question_id>/",
        views.next_question,
        name="next_question",
    ),  # 다음 문제로 이동하는 URL
]
