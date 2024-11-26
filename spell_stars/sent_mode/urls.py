from django.urls import path
from .views import LearningResultListAPIView, LearningResultDetailAPIView
from . import views
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
    ),
    public=True,  # True로 설정하면 인증 없이 접근 가능
    permission_classes=[AllowAny],  # Swagger UI 접근을 모든 사용자에게 허용
)




urlpatterns = [
    path("", views.example_sentence_learning, name="example_sentence_learning"),
    path("upload_audio/", views.upload_audio, name="upload_audio"), 
    path("result/", views.sent_result, name="sent_result"), # 반드시 포함
    path('sent/practice/', views.sent_practice, name='sent_practice'),
    path("next_question/", views.next_question, name="next_question"),
    path('api/learning-results/', LearningResultListAPIView.as_view(), name='learning_results_list'),
    path('api/learning-results/<int:result_id>/', LearningResultDetailAPIView.as_view(), name='learning_results_detail'),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
