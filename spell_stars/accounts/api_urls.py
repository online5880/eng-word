from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from .views import StudentInfoViewSet, StudentLogViewSet, StudentLearningLogViewSet

# Default Router (기본 학생 정보 URL)
router = DefaultRouter()
router.register(r'students', StudentInfoViewSet, basename='students')

# Nested Router (학생 로그 및 학습 로그 URL)
logs_router = NestedDefaultRouter(router, r'students', lookup='student')
logs_router.register(r'logs', StudentLogViewSet, basename='student-logs')
logs_router.register(r'learning-logs', StudentLearningLogViewSet, basename='student-learning-logs')

# URL Patterns
urlpatterns = [
    path('', include(router.urls)),  # 기본 학생 정보 URLs
    path('', include(logs_router.urls)),  # Nested URLs
]
