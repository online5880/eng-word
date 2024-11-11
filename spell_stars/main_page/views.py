# main_page/views.py
from django.shortcuts import render


def home(request):
    return render(request, "home.html")  # 메인 페이지 템플릿을 렌더링
