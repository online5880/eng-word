from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import StudentLog, StudentInfo

@receiver(user_logged_in)
def log_student_login(sender, request, user, **kwargs):
    print("사용자 로그인")  # 디버깅용
    try:
        StudentLog.objects.create(student=user, login_time=timezone.now())
        print("로그인 시간 기록 저장 성공")
    except Exception as e:
        print(f"로그인 시간 기록 저장 실패 : {e}")

@receiver(user_logged_out)
def log_student_logout(sender, request, user, **kwargs):
    print("사용자 로그아웃")  # 디버깅용
    try:
        log = StudentLog.objects.filter(student=user).latest('login_time')
        log.logout_time = timezone.now()
        log.save()
        print("로그아웃 시간 기록 저장 성공")
    except StudentLog.DoesNotExist:
        print("No login log found for logout entry")
    except Exception as e:
        print(f"로그아웃 시간 기록 저장 실패 : {e}")

