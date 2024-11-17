from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm
from .models import StudentInfo
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import StudentInfo, StudentLog, StudentLearningLog
from .serializers import StudentInfoSerializer, StudentLogSerializer, StudentLearningLogSerializer


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

# 학생 학습 로그 ViewSet (GET, POST 전용)
class StudentLearningLogViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    serializer_class = StudentLearningLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # student_pk로 학습 로그 필터링
        student_id = self.kwargs['student_pk']
        return StudentLearningLog.objects.filter(student_id=student_id)

    def perform_create(self, serializer):
        # student_pk로 연결된 학생 가져오기
        student_id = self.kwargs['student_pk']
        student = StudentInfo.objects.get(id=student_id)
        serializer.save(student=student)