# views.py
import json
import os
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import  Word
import whisper
import difflib
from tempfile import NamedTemporaryFile
from faker import Faker
import random
from django.contrib.auth import get_user_model


# Whisper 모델 로드 (애플리케이션 시작 시 한 번만)
model = whisper.load_model("tiny")

def display_vocabulary_book(request):
    
    # User = get_user_model()  # 현재 프로젝트에서 사용하는 User 모델을 가져옴

    words = Word.objects.all()  # 모든 단어 가져오기
    print(words)
    

    return render(request, 'vocab_mode/vocab.html', {'words': words})
