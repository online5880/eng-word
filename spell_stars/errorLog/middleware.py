import logging
import os
import requests
from django.utils.timezone import localtime
from dotenv import load_dotenv

load_dotenv()


class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 에러 상태 코드별 처리
        if response.status_code in [404, 403, 500, 400]:
            self.log_error(request, response)
            self.send_slack_notification(request, response)

        return response

    def log_error(self, request, response):
        logger = logging.getLogger('django')

        # 추가 정보 수집
        client_ip = self.get_client_ip(request)
        method = request.method
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        timestamp = localtime().strftime('%Y-%m-%d %H:%M:%S %Z')  # 지역 시간

        # 사용자 정보
        user_id = getattr(request.user, 'id', 'Anonymous')  # 로그인된 경우 ID
        username = getattr(request.user, 'username', 'Anonymous')  # 로그인된 경우 Username

        # 에러 유형별 메시지
        error_messages = {
            404: "404 Error: {path} not found",
            403: "403 Error: Forbidden access to {path}",
            500: "500 Error: Server error at {path}",
            400: "400 Error: Bad request at {path}",
        }
        log_message = error_messages.get(response.status_code, "Unknown Error").format(path=request.path)

        # 로그 메시지 생성
        log_message += (
            f" | Client IP: {client_ip} | Method: {method} | User-Agent: {user_agent} | "
            f"Timestamp: {timestamp} | User ID: {user_id} | Username: {username}"
        )

        # 로깅 (에러는 ERROR 레벨로 기록)
        logger.error(log_message)

    def send_slack_notification(self, request, response):
        """Slack 웹훅을 통해 에러 알림 전송"""
        webhook_url = os.getenv("WEBHOOK_URL")  # 슬랙 웹훅 URL
        client_ip = self.get_client_ip(request)
        method = request.method
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        timestamp = localtime().strftime('%Y-%m-%d %H:%M:%S %Z')  # 지역 시간

        # 사용자 정보
        user_id = getattr(request.user, 'id', 'Anonymous')  # 로그인된 경우 ID
        username = getattr(request.user, 'username', 'Anonymous')  # 로그인된 경우 Username

        # 메시지 템플릿
        error_messages = {
            404: "404 Error: {path} not found",
            403: "403 Error: Forbidden access to {path}",
            500: "500 Error: Server error at {path}",
            400: "400 Error: Bad request at {path}",
        }
        error_message = error_messages.get(response.status_code, "Unknown Error").format(path=request.path)

        # Slack 메시지 페이로드
        payload = {
            "text": f"⚠️ {error_message}",
            "attachments": [
                {
                    "color": "#ff0000",  # 빨간색 표시
                    "fields": [
                        {"title": "Status Code", "value": response.status_code, "short": True},
                        {"title": "Path", "value": request.path, "short": True},
                        {"title": "Client IP", "value": client_ip, "short": True},
                        {"title": "Method", "value": method, "short": True},
                        {"title": "User-Agent", "value": user_agent, "short": False},
                        {"title": "User ID", "value": user_id, "short": True},
                        {"title": "Username", "value": username, "short": True},
                        {"title": "Timestamp", "value": timestamp, "short": False},
                    ],
                }
            ],
        }

        # Slack 웹훅 호출
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.getLogger('django').error(f"Slack webhook failed: {e}")

    def get_client_ip(self, request):
        """요청에서 클라이언트 IP를 추출합니다."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')