from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sent/", include("sent_mode.urls")),  # sent_mode를 /sent/에 연결
]
