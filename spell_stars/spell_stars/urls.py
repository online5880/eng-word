"""
URL configuration for spell_stars project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as mainViews
from vocab_mode import views as vocabViews
from test_mode import views as testViews
from pron_practice import views as pronViews
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API",
      default_version='v1',
      description="API 문서",
    #   terms_of_service="https://www.google.com/policies/terms/",
    #   contact=openapi.Contact(email="contact@example.com"),
    #   license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # 메인 페이지
    path("", mainViews.index, name="index"),
    
    # 사용자 인증 및 계정 관련 URL
    path("account/", include("accounts.urls")),  # accounts 앱의 URL 패턴
    path("accounts/", include("django.contrib.auth.urls")),  # Django의 기본 인증 URL
    
    # 학습 모드 및 기타 기능 URL
    path("vocab_mode/", include("vocab_mode.urls")),
    path("test_mode/", include("test_mode.urls")),
    path("pron_practice/", include("pron_practice.urls")),
    
    # API 문서
    path('swagger/v1/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/v1/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("account/v1/",include("accounts.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
