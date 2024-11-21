import logging
from django.utils.timezone import localtime

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 에러 상태 코드별 처리
        if response.status_code in [404, 403, 500, 400]:
            self.log_error(request, response)

        return response

    def log_error(self, request, response):
        logger = logging.getLogger('django')

        # 추가 정보 수집
        client_ip = self.get_client_ip(request)
        method = request.method
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        timestamp = localtime().strftime('%Y-%m-%d %H:%M:%S %Z')  # 지역 시간

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
            f"Timestamp: {timestamp}"
        )

        # 로깅 (에러는 ERROR 레벨로 기록)
        logger.error(log_message)

    def get_client_ip(self, request):
        """요청에서 클라이언트 IP를 추출합니다."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
