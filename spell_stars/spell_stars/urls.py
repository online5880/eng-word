from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as mainViews
from django.views.generic.base import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.views import export_students, export_learning_results, export_test_results
from django.conf.urls import handler404, handler500, handler403
from vocab_mode import views as vocab_views
from sent_mode import views as sent_views

# API 문서 스키마 설정
schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API 문서",
    ),
    public=True,
    permission_classes=(IsAuthenticated,),
)

# API URL 패턴
api_v1_patterns = [
    path("accounts/", include("accounts.api_urls")),
    path("vocab/", include("vocab_mode.api_urls")),
    path("test/", include("test_mode.api_urls")),
    path("sent/",include("sent_mode.api_urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path('pronunciation-checker-api/',vocab_views.PronunciationCheckerAPIView.as_view(),name='pronunciation-checker-api'), # 발음 검사기 API
    path('answer-checker-api/', sent_views.AnswerCheckerAPIView.as_view(), name='answer-checker-api'),
]

# 웹 URL 패턴
urlpatterns = [
    path("admin/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "images/favicon.ico")),
    path("", mainViews.index, name="index"),
    path("accounts/", include("accounts.urls")),
    path("vocab/", include("vocab_mode.urls")),
    path("test/", include("test_mode.urls")),
    path("practice/", include("pron_practice.urls")),
    path("sent/", include("sent_mode.urls")),
    path("api/v1/", include(api_v1_patterns)),
    path('dashboard/', include('dashboard.urls')),
    
    # 데이터 추출 URL패턴
    path('export/students/', export_students, name='export_students'),                          # 학생 목록
    path('export/learning-results/', export_learning_results, name='export_learning_results'),  # 학습 결과 목록
    path('export/test-results/', export_test_results, name='export_test_results'),              # 시험 결과 목록
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'spell_stars.views.error_404'
handler500 = 'spell_stars.views.error_500'
handler403 = 'spell_stars.views.error_403'