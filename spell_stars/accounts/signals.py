from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import StudentLog, Student

@receiver(user_logged_in)
def log_student_login(sender, request, user, **kwargs):
    print("사용자 로그인")
    try:
        if user.role == 'student':
            student = Student.objects.get(user=user)
            StudentLog.objects.create(
                student=student,
                login_time=timezone.now()
            )
            print("로그인 시간 기록 저장 성공")
    except Student.DoesNotExist:
        print("학생 프로필을 찾을 수 없습니다.")
    except Exception as e:
        print(f"로그인 시간 기록 저장 실패: {e}")

@receiver(user_logged_out)
def log_student_logout(sender, request, user, **kwargs):
    print("사용자 로그아웃")
    try:
        if user.role == 'student':
            student = Student.objects.get(user=user)
            log = StudentLog.objects.filter(student=student).latest('login_time')
            log.logout_time = timezone.now()
            log.save()
            print("로그아웃 시간 기록 저장 성공")
    except Student.DoesNotExist:
        print("학생 프로필을 찾을 수 없습니다.")
    except StudentLog.DoesNotExist:
        print("로그인 기록을 찾을 수 없습니다.")
    except Exception as e:
        print(f"로그아웃 시간 기록 저장 실패: {e}")

