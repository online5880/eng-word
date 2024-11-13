from django.db import models
from accounts.models import User  # 사용자 모델 연결
from vocab_mode.models import Word
from sent_mode.models import Sentence
import datetime


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자 연결
    word = models.ForeignKey(Word, on_delete=models.CASCADE)  # 단어 연결
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)  # 예문 연결
    score = models.IntegerField()  # 점수
    test_date = models.DateTimeField(default=datetime.datetime.now)  # 시험 날짜

    def __str__(self):
        return f"{self.user.username} - {self.score}점 - {self.test_date}"
