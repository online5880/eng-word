from django.db import models
from vocab_mode.models import Word  # vocab_mode에서 단어 정보 참조
from accounts.models import Student  # 학생 정보 참조


# 예문(LLM) 테이블
class Sentence(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    sentence = models.TextField()
    sentence_meaning = models.TextField()

    def __str__(self):
        return self.sentence


class LearningResult(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    learning_category = models.IntegerField()  # 단어 카테고리 번호
    learning_date = models.DateTimeField()
    pronunciation_score = models.IntegerField()
    accuracy_score = models.IntegerField()
    frequency_score = models.IntegerField()
