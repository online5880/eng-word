"""
Django settings for spell_stars project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import dotenv

path = dotenv.find_dotenv()

dotenv.load_dotenv(override=True)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-d)nsnf#(h_rxv=vod-adjyj#jlv$tky9+ve-$b&g3hdq5)*@w-"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    # 'https://a0d0-121-140-172-195.ngrok-free.app',
]

# Application definition

INSTALLED_APPS = [
    # 기본 Django 앱들
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 커스텀 앱들
    "main",
    "sent_mode",
    "pron_practice",
    "test_mode",
    "vocab_mode",
    "rest_framework",
    "drf_yasg",
    "accounts",
    "channels",

]

ASGI_APPLICATION = 'spell_stars.asgi.application'

# Channels Layer 설정 (기본적으로 In-Memory 사용, Redis를 권장)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": [],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'accounts.middleware.UpdateLastLoginMiddleware',
    'accounts.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = "spell_stars.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "spell_stars.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("NAME"),
        "USER": os.getenv("USERNAME"),
        "PASSWORD": os.getenv("PASSWORD"),
        "HOST": os.getenv("HOST"),
        "PORT": os.getenv("PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.StudentInfo"

LOGIN_URL = "/accounts/login/"  # @login_required가 리디렉션할 로그인 URL
LOGOUT_URL = "/accounts/logout/"  # 로그아웃 버튼이나 링크가 사용할 로그아웃 URL
LOGIN_REDIRECT_URL = "/"  # 로그인 후 리디렉션될 URL
LOGOUT_REDIRECT_URL = "/"  # 로그아웃 후 메인 페이지로 리디렉션

MEDIA_URL = "/media/"  # URL로 접근할 때 사용할 경로
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # 실제 파일이 저장될 경로

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 브라우저 닫으면 세션 종료
SESSION_COOKIE_AGE = 600  # 세션 만료 시간 (초 단위, 여기선 1시간)
