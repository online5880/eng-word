from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth import logout
from django.utils.timezone import now
from django.urls import reverse
from django.http import HttpResponseRedirect

from accounts.models import StudentLog, Student
from datetime import datetime, timedelta
import pytz


# 마지막 접속 시간 한국 시간으로 업데이트
class UpdateLastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 사용자가 인증된 경우 last_login을 한국 시간대로 업데이트
        if request.user.is_authenticated:
            seoul_timezone = pytz.timezone("Asia/Seoul")
            # 한국 시간으로 변환하여 DB에 저장
            request.user.last_login = timezone.now().astimezone(seoul_timezone)
            request.user.save(update_fields=['last_login'])

        return response

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if last_activity:
                # 문자열을 datetime 객체로 변환
                last_activity_time = datetime.fromisoformat(last_activity)
                # 세션 만료 확인
                if now() > last_activity_time + timedelta(seconds=request.session.get('timeout', 1800)):
                    self.record_logout(request)
                    logout(request)
                    request.session.flush()
                    return self.redirect_to_login()

            # 마지막 활동 시간 갱신
            request.session['last_activity'] = now().isoformat()

        return self.get_response(request)

    def record_logout(self, request):
        """
        StudentLog에 로그아웃 시간을 기록합니다.
        """
        try:
            if request.user.role == 'student':
                student = Student.objects.get(user=request.user)
                log = StudentLog.objects.filter(student=student).latest('login_time')
                log.logout_time = now()
                log.save()
        except Student.DoesNotExist:
            print("학생 프로필을 찾을 수 없습니다.")
        except StudentLog.DoesNotExist:
            print("로그인 기록을 찾을 수 없습니다.")
        except Exception as e:
            print(f"로그아웃 시간 기록 저장 실패: {e}")
        finally:
            print("로그아웃 프로세스 완료")

    def redirect_to_login(self):
        return HttpResponseRedirect(reverse('login'))