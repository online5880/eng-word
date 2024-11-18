from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import StudentLog, StudentInfo

@receiver(user_logged_in)
def log_student_login(sender, request, user, **kwargs):
    print("User logged in")  # 디버깅용
    try:
        StudentLog.objects.create(student=user, login_time=timezone.now())
        print("Login time recorded successfully")
    except Exception as e:
        print(f"Error in recording login time: {e}")

@receiver(user_logged_out)
def log_student_logout(sender, request, user, **kwargs):
    print("User logged out")  # 디버깅용
    try:
        log = StudentLog.objects.filter(student=user).latest('login_time')
        log.logout_time = timezone.now()
        log.save()
        print("Logout time recorded successfully")
    except StudentLog.DoesNotExist:
        print("No login log found for logout entry")
    except Exception as e:
        print(f"Error in recording logout time: {e}")

