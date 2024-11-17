from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as mainViews

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

# API 문서 스키마 설정
schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API 문서",
    ),
    public=False,  # 인증된 사용자만 접근
    permission_classes=(IsAuthenticated,),
)

urlpatterns = [
    # 관리자 URL
    path("admin/", admin.site.urls),

    # 메인 페이지
    path("", mainViews.index, name="index"),

    # 사용자 인증 및 계정 관련 URL
    path("accounts/", include("accounts.urls")),  # 사용자 정의 계정 관련 URL
    path("auth/", include("django.contrib.auth.urls")),  # Django 기본 인증 URL

    # 학습 모드 및 기타 기능 URL
    path("vocab/", include("vocab_mode.urls")),  # 단어 학습 모드
    path("test/", include("test_mode.urls")),  # 테스트 모드
    path("practice/", include("pron_practice.urls")),  # 발음 연습 모드

    # API 문서 URL
    path("api/v1/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/v1/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # API 엔드포인트
    path("api/v1/accounts/", include("accounts.api_urls")),  # API를 위한 계정 URL
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)