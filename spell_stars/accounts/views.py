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
from django.contrib import messages

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
            messages.success(request, "회원가입 완료!")
            return redirect("/")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profileView(request):
    return render(request, "accounts/profile.html", {"user": request.user})



# API Views
class StudentInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    학생 기본 정보를 조회하는 API
    - GET /api/students/ : 전체 학생 목록 조회
    - GET /api/students/{id}/ : 특정 학생 정보 조회
    """
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = [IsAuthenticated]

class StudentLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    학생의 활동 로그를 조회하는 API
    - GET /api/students/{student_pk}/logs/ : 특정 학생의 전체 로그 조회
    """
    serializer_class = StudentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentLog.objects.filter(student_id=self.kwargs['student_pk'])

class StudentLearningLogViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.UpdateModelMixin,
                               viewsets.GenericViewSet):
    """
    학생의 학습 로그를 관리하는 API
    - GET /api/students/{student_pk}/learning-logs/ : 학습 로그 목록 조회
    - POST /api/students/{student_pk}/learning-logs/ : 새로운 학습 로그 생성
    - PATCH /api/students/{student_pk}/learning-logs/{id}/end_log/ : 학습 종료 시간 기록
    """
    serializer_class = StudentLearningLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StudentLearningLog.objects.none()
        student_id = self.kwargs.get('student_pk')
        if not student_id:
            raise ValueError("student_pk는 필수 파라미터입니다")
        return StudentLearningLog.objects.filter(student_id=student_id)

    def perform_create(self, serializer):
        student = StudentInfo.objects.get(id=self.kwargs.get('student_pk'))
        serializer.save(student=student)

    @action(detail=True, methods=['patch'])
    def end_log(self, request, student_pk=None, pk=None):
        """학습 종료 시간을 기록하는 메서드"""
        try:
            log = self.get_object()
            serializer = self.get_serializer(log, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(end_time=request.data.get('end_time', timezone.now()))
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# 학습 세션 관리를 위한 함수형 뷰
def start_learning_session(request, learning_mode):
    """
    학습 세션을 시작하고 세션 ID를 저장하는 뷰
    """
    current_time = timezone.now()
    data = {
        "student": request.user.id,
        "learning_mode": learning_mode,
        "start_time": current_time,
    }
    serializer = StudentLearningLogSerializer(data=data)
    if serializer.is_valid():
        log = serializer.save()
        request.session["learning_log_id"] = log.id
        return JsonResponse({"status": "success", "log_id": log.id})
    return JsonResponse({"status": "error", "errors": serializer.errors}, status=400)

def end_learning_session(request):
    """
    진행 중인 학습 세션을 종료하는 뷰
    """
    log_id = request.session.get("learning_log_id")
    if not log_id:
        return JsonResponse({"status": "error", "message": "진행 중인 학습 세션이 없습니다"}, status=400)

    try:
        log = StudentLearningLog.objects.get(id=log_id, student=request.user)
        log.end_time = timezone.now()
        log.save()
        del request.session["learning_log_id"]
        return JsonResponse({"status": "success"})
    except StudentLearningLog.DoesNotExist:
        return JsonResponse({"status": "error", "message": "유효하지 않은 학습 로그입니다"}, status=400)