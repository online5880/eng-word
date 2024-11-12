from django.urls import path
from . import views

urlpatterns = [
    path("", views.pronunciation_practice_view, name="pron_practice"),
    path("next_word/", views.next_word, name="next_word"),
    path(
        "evaluate_pronunciation/",
        views.evaluate_pronunciation,
        name="evaluate_pronunciation",
    ),  # 음성 인식 평가
]
