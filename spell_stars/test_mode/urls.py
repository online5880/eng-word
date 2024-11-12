from django.urls import path
from . import views

urlpatterns = [
    path("test_mode/", views.test_mode_view, name="test_mode"),
    path(
        "recognize_audio/<int:question_id>/",
        views.recognize_audio,
        name="recognize_audio",
    ),
]
