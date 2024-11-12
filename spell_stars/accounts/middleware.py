from django.utils import timezone
import pytz

# 마지막 접속 시간 한국 시간으로 변경
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
