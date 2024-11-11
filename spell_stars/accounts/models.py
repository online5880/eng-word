from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(verbose_name="닉네임",max_length=30,blank=True) # 닉네임 필드
    age = models.PositiveIntegerField(
        verbose_name="나이",
        blank=True,
        null=True,
        validators=[MinValueValidator(5),MaxValueValidator(100)] # 최소, 최대
    )
    
    def __str__(self):
        return self.username