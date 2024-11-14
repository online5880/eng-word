from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

# Create your models here.


# 학생 기본 정보 테이블
class StudentInfo(AbstractUser):
    pass

    def __str__(self):
        return self.name

    # 나이 계산
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )


# 학생 로그 데이터 테이블
class StudentLog(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField()


# 학생 학습 로그 데이터 테이블
class StudentLearningLog(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    learning_mode = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
