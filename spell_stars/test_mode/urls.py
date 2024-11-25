from django.urls import path
from . import views
from .views import TestResultListAPIView, TestResultDetailAPIView

urlpatterns = [
    path("", views.test_mode_view, name="test_mode"),
    path("submit_audio/", views.submit_audio, name="submit_audio"),
    path("next_question/", views.next_question, name="next_question"),
    path("results/", views.results_view, name="results"),
]
