from django.urls import path
from . import views
from .views import TestResultListAPIView, TestResultDetailAPIView

urlpatterns = [
    # API URL 추가
    path("test-results/", TestResultListAPIView.as_view(), name="test-results"),
    path("test-results/<int:test_id>/", TestResultDetailAPIView.as_view(), name="test-result-details"),
]