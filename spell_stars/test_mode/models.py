import datetime
from django.db import models
from accounts.models import StudentInfo


class TestResult(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    test_number = models.IntegerField()
    test_date = models.DateTimeField()
    accuracy_score = models.IntegerField()
