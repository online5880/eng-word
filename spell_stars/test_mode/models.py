from django.db import models
from accounts.models import Student
from vocab_mode.models import Word
from sent_mode.models import Sentence

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_number = models.IntegerField()
    test_date = models.DateTimeField(auto_now_add=True)
    accuracy_score = models.FloatField()

class TestResultDetail(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name="details")
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    sentence = models.TextField()
    sentence_meaning = models.TextField()
    is_correct = models.BooleanField()
