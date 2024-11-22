import logging
import traceback
from django.apps import apps

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        # 모델을 동적으로 가져오기
        ErrorLog = apps.get_model('errorLog', 'ErrorLog')

        # traceback 정보 처리
        exc_text = None
        if record.exc_info:
            exc_text = ''.join(traceback.format_exception(*record.exc_info))

        try:
            ErrorLog.objects.create(
                level=record.levelname,
                message=record.getMessage(),
                traceback=exc_text,
            )
        except Exception:
            # 로깅 에러는 무시
            pass