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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("accounts.urls")),
    path("", mainViews.index, name="index"),
    path(
        "accounts/", include("django.contrib.auth.urls")
    ),  # Django의 기본 인증 URL 패턴 추가
    path("vocab_mode/", vocabViews.word_learning_view, name="vocab_mode"),
    path("test_mode/", testViews.test_mode_view, name="test_mode"),
    path(
        "pron_practice/",
        pronViews.pronunciation_practice_view,
        name="pron_practice",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
