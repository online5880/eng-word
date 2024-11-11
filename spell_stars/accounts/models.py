from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(verbose_name="닉네임", max_length=30, blank=True)  # 닉네임 필드
    birth_date = models.DateField(verbose_name="생년월일", blank=True, null=True)  # 생년월일 필드
    
    def __str__(self):
        return self.username
    
    # 나이 계산
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )