from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(max_length=30,blank=True) # 닉네임 필드
    
    def __str__(self):
        return self.username