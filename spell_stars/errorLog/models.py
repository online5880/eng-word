from django.db import models

class ErrorLog(models.Model):
    level = models.CharField(max_length=50)  # 로그 수준 (예: ERROR, WARNING)
    message = models.TextField()            # 에러 메시지
    traceback = models.TextField(blank=True, null=True)  # 스택 트레이스
    created_at = models.DateTimeField(auto_now_add=True) # 로그 시간

    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"
