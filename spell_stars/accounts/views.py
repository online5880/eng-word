from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm
from .models import StudentInfo
from rest_framework.decorators import action
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StudentInfo, StudentLog, StudentLearningLog
from .serializers import StudentInfoSerializer, StudentLogSerializer, StudentLearningLogSerializer
from django.http import JsonResponse
from datetime import datetime
from rest_framework.test import APIRequestFactory
from django.utils import timezone

# Create your views here.

# 로그인뷰
class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm


class UserLogoutView(LogoutView):
    next_page = "/"


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("/")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profileView(request):
    return render(request, "accounts/profile.html", {"user": request.user})



# API
# 학생 기본 정보 ViewSet (GET 전용)
class StudentInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

# 학생 로그 ViewSet (GET, POST 전용)
class StudentLogViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = StudentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # student_pk로 학생 로그 필터링
        student_id = self.kwargs['student_pk']
        return StudentLog.objects.filter(student_id=student_id)

    def perform_create(self, serializer):
        # student_pk로 연결된 학생 가져오기
        student_id = self.kwargs['student_pk']
        student = StudentInfo.objects.get(id=student_id)
        serializer.save(student=student)

class StudentLearningLogViewSet(mixins.CreateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    """
    학생 학습 로그 ViewSet
    학습 시작(Create), 학습 종료(Update)을 처리
    """
    serializer_class = StudentLearningLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        학생의 학습 로그만 필터링
        """
        student_id = self.kwargs['student_pk']
        return StudentLearningLog.objects.filter(student_id=student_id)

    def perform_create(self, serializer):
        """
        학습 로그 생성 시 student_id를 연결
        """
        student_id = self.kwargs['student_pk']
        student = StudentInfo.objects.get(id=student_id)
        serializer.save(student=student)

    @action(detail=True, methods=['patch'])
    def end_log(self, request, student_pk=None, pk=None):
        """학습 로그 종료 처리"""
        try:
            log = self.get_object()
            log.end_time = request.data.get('end_time')
            log.save()
            serializer = self.get_serializer(log)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )


def start_learning_session(request, learning_mode):
    """학습 세션 시작"""
    factory = APIRequestFactory()
    current_time = timezone.now()
    api_request = factory.post(
        f"/api/students/{request.user.id}/learning-logs/",
        {
            "student": request.user.id,
            "learning_mode": learning_mode,
            "start_time": current_time.isoformat(),
            "end_time": current_time.isoformat(),
        },
    )
    api_request.user = request.user
    view = StudentLearningLogViewSet.as_view({"post": "create"})
    
    response = view(api_request, student_pk=request.user.id)
    
    if response.status_code == 201:
        log_id = response.data.get("id")
        request.session["learning_log_id"] = log_id
        print(f"학습 로그 생성 성공 (ID: {log_id})")
        return JsonResponse({"status": "success", "log_id": log_id})
    print(f"학습 로그 생성 실패: {response.status_code}, {response.data}")
    return JsonResponse({"status": "error"}, status=400)

def end_learning_session(request):
    """학습 세션 종료"""
    log_id = request.session.get("learning_log_id")
    if not log_id:
        return JsonResponse({"status": "error", "message": "No active learning session"}, status=400)
    
    factory = APIRequestFactory()
    api_request = factory.patch(
        f"/students/{request.user.id}/learning-logs/{log_id}/end_log/",
        {
            "end_time": timezone.now().isoformat(),
        },
    )
    api_request.user = request.user
    view = StudentLearningLogViewSet.as_view({"patch": "end_log"})
    
    try:
        response = view(api_request, student_pk=request.user.id, pk=log_id)
        if response.status_code == 200:
            del request.session["learning_log_id"]
            print(f"학습 로그 종료 성공 (ID: {log_id})")
            return JsonResponse({"status": "success"})
    except Exception as e:
        print(f"학습 로그 종료 실패: {str(e)}")
    
    return JsonResponse({"status": "error"}, status=400)