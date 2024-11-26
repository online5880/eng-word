from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from .views import ParentStudentRelationViewSet, StudentViewSet, StudentLogViewSet, StudentLearningLogViewSet,ParentViewSet

# 기본 라우터
router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'parent-student-relations', ParentStudentRelationViewSet, basename='parent-student-relation')
router.register(r'parents', ParentViewSet)

# 학생별 하위 라우터
students_router = NestedSimpleRouter(router, r'students', lookup='student')
students_router.register(r'logs', StudentLogViewSet, basename='student-logs')
students_router.register(r'learning-logs', StudentLearningLogViewSet, basename='student-learning-logs')


# URL 패턴
urlpatterns = [
    path('', include(router.urls)),  # 학생 관련 URL
    path('', include(students_router.urls)),  # 학생 하위 리소스 URL
]
