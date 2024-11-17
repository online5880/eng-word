from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

# Create your models here.


# 학생 기본 정보 테이블
class StudentInfo(AbstractUser):
    birth_date = models.DateField(verbose_name="생년월일", blank=True, null=True)  # 생년월일 필드
    grade = models.IntegerField(choices=[(i, f"{i}학년") for i in range(1, 7)], verbose_name="학년", blank=True, null=True, default=1)  # 1학년부터 6학년 선택 필드
    name = models.CharField(max_length=30, verbose_name="이름", blank=False, default="이름 없음")  # 이름 필드 추가
    # def __str__(self):
    #     return self.name

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
    
    # 학년 계산        
    @property
    def derived_grade(self):
        age = self.age
        if age is None:
            return None  # 생년월일이 없을 경우 학년을 계산하지 않음
        elif 8 <= age <= 13:  # 1학년부터 6학년
            return age - 7
        return None  # 나이가 학년 범위에 맞지 않을 경우 None 반환


# 학생 로그 데이터 테이블
class StudentLog(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True) 


# 학생 학습 로그 데이터 테이블
class StudentLearningLog(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    learning_mode = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True) 
