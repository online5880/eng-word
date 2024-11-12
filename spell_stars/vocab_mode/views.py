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

# Whisper 모델 로드 (애플리케이션 시작 시 한 번만)
model = whisper.load_model("base")

def display_vocabulary_book(request, book_id):
    # book_id에 해당하는 VocabularyBook 객체 조회
    vocabulary_book = get_object_or_404(VocabularyBook, id=book_id)
    word_data = vocabulary_book.words.all()  # VocabularyBook의 words 가져오기

    return render(request, 'display_vocabulary.html', {'words': word_data, 'book': vocabulary_book})

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
