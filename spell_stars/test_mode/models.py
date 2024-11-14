import datetime
from django.db import models
from accounts.models import User

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자 연결
    test_number = models.IntegerField()  # 시험 번호
    score = models.IntegerField()  # 점수
    test_date = models.DateTimeField(default=datetime.datetime.now)  # 시험 날짜

    def __str__(self):
        return f"{self.user.username} - {self.score}점 - {self.test_date}"
