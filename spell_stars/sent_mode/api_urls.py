from django.urls import path
from .views import LearningResultListAPIView, LearningResultDetailAPIView, AnswerCheckerAPIView

urlpatterns = [
    path('learning-results/', LearningResultListAPIView.as_view(), name='learning_results_list'),
    path('learning-results/<int:result_id>/', LearningResultDetailAPIView.as_view(), name='learning_results_detail'),
]
