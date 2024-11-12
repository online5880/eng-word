# views.py
import json
import os
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import VocabularyBook, Word, PronunciationRecord
import whisper
import difflib
from tempfile import NamedTemporaryFile
from faker import Faker
import random
from django.contrib.auth import get_user_model


# Whisper 모델 로드 (애플리케이션 시작 시 한 번만)
model = whisper.load_model("tiny")

def display_vocabulary_book(request):
    
    User = get_user_model()  # 현재 프로젝트에서 사용하는 User 모델을 가져옴
    
    words = Word.objects.all()  # 모든 단어 가져오기

    return render(request, 'vocab_mode/word_learning.html', {'words': words})

def load_words_from_json(json_path):
    # JSON 파일 열기
    with open(json_path, 'r', encoding='utf-8') as file:  # 파일 인코딩에 맞춰 조정
        words = json.load(file)

    # 각 단어를 데이터베이스에 저장
    for word_text in words:
        Word.objects.create(text=word_text)
    print("단어들이 데이터베이스에 성공적으로 저장되었습니다.")

@csrf_exempt
def evaluate_pronunciation(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        word_id = request.POST.get('word_id')
        word = get_object_or_404(Word, id=word_id)
        uploaded_audio = request.FILES['audio']

        # 임시 파일에 저장
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            for chunk in uploaded_audio.chunks():
                temp_audio_file.write(chunk)
            temp_audio_path = temp_audio_file.name

        try:
            # Whisper로 STT 처리
            result = model.transcribe(temp_audio_path)
            student_text = result['text'].strip()

            # 유사도 계산
            target_text = word.text.strip()
            similarity_score = difflib.SequenceMatcher(None, student_text, target_text).ratio() * 100

            # PronunciationRecord 저장
            student = request.user  # 현재 로그인한 사용자
            pronunciation_record = PronunciationRecord.objects.create(
                word=word,
                student=student,
                score=similarity_score,
                audio_file=uploaded_audio
            )

            return JsonResponse({
                'original_text': target_text,
                'student_text': student_text,
                'score': similarity_score,
                'success': True
            })
        finally:
            # 임시 파일 삭제
            os.remove(temp_audio_path)
