from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from rest_framework import status
from .forms import LoginForm, SignupForm, AddChildForm
from .models import ParentStudentRelation, Student, Parent,StudentLearningLog, StudentLog
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ParentStudentRelationSerializer, StudentSerializer, StudentLogSerializer, StudentLearningLogSerializer, ParentSerializer
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views import View
from test_mode.models import TestResult
from django.core.exceptions import ValidationError
from django.db import transaction

# 로그인뷰
class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm


class UserLogoutView(LogoutView):
    next_page = "/"


class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                messages.success(request, "계정이 성공적으로 생성되었습니다.")
                return redirect('login')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"계정 생성 중 오류가 발생했습니다: {str(e)}")
        
        return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profileView(request):
    if request.method == "POST" and request.user.role == 'parent':
        form = AddChildForm(request.POST)
        if form.is_valid():
            student_code = form.cleaned_data['student_code']
            parent_relation = form.cleaned_data['parent_relation']
            
            try:
                student = Student.objects.get(unique_code=student_code)
                parent = request.user.parent_profile
                
                if ParentStudentRelation.objects.filter(parent=parent, student=student).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': "이미 등록된 자녀입니다."
                    })
                
                ParentStudentRelation.objects.create(
                    parent=parent,
                    student=student,
                    parent_relation=parent_relation
                )
                return JsonResponse({
                    'status': 'success',
                    'message': "자녀가 성공적으로 등록되었습니다."
                })
            except Student.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': "유효하지 않은 학생 코드입니다."
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f"오류가 발생했습니다: {str(e)}"
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': "입력값이 올바르지 않습니다."
            })

    form = AddChildForm()
    context = {
        'user': request.user,
        'add_child_form': form if request.user.role == 'parent' else None
    }
    return render(request, "accounts/profile.html", context)

# API Views
class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    학생 기본 정보를 조회하는 API
    - GET /api/students/ : 전체 학생 목록 조회
    - GET /api/students/{id}/ : 특정 학생 정보 조회
    """
    queryset = Student.objects.select_related('user').all()  # `user`와 함께 가져오기 최적화
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    학생의 활동 로그를 조회하는 API
    - GET /api/students/{student_pk}/logs/ : 특정 학생의 전체 로그 조회
    """
    serializer_class = StudentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 학생 ID를 기반으로 로그 필터링
        student_pk = self.kwargs.get('student_pk')
        return StudentLog.objects.filter(student_id=student_pk)
    
class ParentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    학부모 기본 정보를 조회하는 API
    - GET /api/parents/ : 전체 학부모 목록 조회
    - GET /api/parents/{id}/ : 특정 학부모 정보 조회
    """
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Parent.objects.all()
        


class StudentLearningLogViewSet(viewsets.ModelViewSet):
    """
    학생의 학습 로그를 관리하는 API
    - GET /api/students/{student_pk}/learning-logs/ : 학습 로그 목록 조회
    - POST /api/students/{student_pk}/learning-logs/ : 새로운 학습 로그 생성
    - PATCH /api/students/{student_pk}/learning-logs/{id}/end_log/ : 학습 종료 시간 기록
    """
    serializer_class = StudentLearningLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']  # DELETE 제외

    def get_queryset(self):
        # 학생 ID를 기반으로 학습 로그 필터링
        student_pk = self.kwargs.get('student_pk')
        return StudentLearningLog.objects.filter(student_id=student_pk)

    @action(detail=True, methods=['patch'], url_path='end-log')
    def end_log(self, request, *args, **kwargs):
        """
        학습 종료 시간을 기록하는 커스텀 액션
        """
        log = self.get_object()  # 해당 학습 로그 객체 가져오기
        log.end_time = request.data.get('end_time')  # 종료 시간 업데이트
        log.save()
        serializer = self.get_serializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ParentStudentRelationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    학부모-학생 관계 조회 API
    - GET /api/parent-student-relations/ : 모든 학부모-학생 관계 조회
    - GET /api/parent-student-relations/{id}/ : 특정 관계 조회
    """
    queryset = ParentStudentRelation.objects.select_related('parent__user', 'student__user').all()
    serializer_class = ParentStudentRelationSerializer
    permission_classes = [IsAuthenticated]  # 인증 필요 시 [IsAuthenticated] 추가

# 학습 세션 관리를 위한 함수형 뷰
def start_learning_session(request, learning_mode):
    """
    학습 세션을 시작하고 세션 ID를 저장하는 뷰
    """
    try:
        student = Student.objects.get(user=request.user)
        current_time = timezone.now()
        data = {
            "student": student.id,
            "learning_mode": learning_mode,
            "start_time": current_time,
        }
        print("학생 정보 : ",data)
        serializer = StudentLearningLogSerializer(data=data)
        if serializer.is_valid():
            log = serializer.save()
            request.session["learning_log_id"] = log.id
            print("학습 세션이 시작되었습니다. session id:",request.session["learning_log_id"])
            return JsonResponse({"status": "success", "log_id": log.id})
        
        print("학습 세션이 시작 실패",request.session["learning_log_id"])
        return JsonResponse({"status": "error", "errors": serializer.errors}, status=400)
    except Student.DoesNotExist:
        return JsonResponse({"status": "error", "message": "학생 프로필을 찾을 수 없습니다"}, status=400)

def end_learning_session(request):
    """
    진행 중인 학습 세션을 종료하는 뷰
    """
    log_id = request.session.get("learning_log_id")
    if not log_id:
        return JsonResponse({"status": "error", "message": "진행 중인 학습 세션이 없습니다"}, status=400)

    try:
        student = Student.objects.get(user=request.user)
        log = StudentLearningLog.objects.get(id=log_id, student=student)
        log.end_time = timezone.now()
        log.save()
        
        # 세션에서 learning_log_id 삭제
        print("학습 세션이 종료되었습니다. session id:",request.session["learning_log_id"])
        del request.session["learning_log_id"]
        
        return JsonResponse({
            "status": "success",
            "message": "학습 세션이 종료되었습니다"
        })
    except Student.DoesNotExist:
        return JsonResponse({
            "status": "error", 
            "message": "학생 프로필을 찾을 수 없습니다"
        }, status=400)
    except StudentLearningLog.DoesNotExist:
        return JsonResponse({
            "status": "error", 
            "message": "유효하지 않은 학습 로그입니다"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"오류가 발생했습니다: {str(e)}"
        }, status=400)
    
    
    
    
    
    
def student_learning_history(request, student_id):
    # 권한 확인
    if request.user.role != 'parent':
        messages.error(request, "학부모만 접근할 수 있습니다.")
        return redirect('profile')
        
    student = get_object_or_404(Student, id=student_id)
    
    # 해당 학부모가 이 학생과 연결되어 있는지 확인
    if not student.parents.filter(user=request.user).exists():
        messages.error(request, "접근 권한이 없습니다.")
        return redirect('profile')
    
    # 학습 데이터 가져오기
    test_results = TestResult.objects.filter(student=student).order_by('-test_date')
    learning_logs = StudentLearningLog.objects.filter(student=student).order_by('-start_time')
    
    context = {
        'student': student,
        'test_results': test_results,
        'learning_logs': learning_logs,
    }
    
    return render(request, 'accounts/student_learning_history.html', context)