# views.py

import logging
from django.http import HttpResponse
logger = logging.getLogger('project_logger')    

# 'project_logger'라는 로거 사용

def log_test(request):
    # 다양한 로깅 수준에서 메시지 기록
    # logger.debug("This is a debug message")
    # logger.info("This is an info message")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")
    # logger.critical("This is a critical message")
    division_by_zero = 1 / 0  # ZeroDivisionError 발생
    return HttpResponse("This won't be reached due to error.")