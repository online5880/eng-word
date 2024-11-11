import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import VocabularyBook, Word
import whisper
import difflib

# Whisper 모델 로드
model = whisper.load_model("base")

def display_vocabulary_book(request, book_id):
    vocabulary_book = get_object_or_404(VocabularyBook, id=book_id)

    # JSON 파일에서 데이터를 읽어옴
    if vocabulary_book.json_file:
        with open(vocabulary_book.json_file.path, 'r', encoding='utf-8') as file:
            word_data = json.load(file)
    else:
        word_data = []

    return render(request, 'display_vocabulary.html', {'words': word_data, 'book': vocabulary_book})

@csrf_exempt
def evaluate_pronunciation(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        word_id = request.POST.get('word_id')
        word = get_object_or_404(Word, id=word_id)
        uploaded_audio = request.FILES['audio']

        # 임시 파일에 저장
        with open('temp_audio.wav', 'wb') as f:
            for chunk in uploaded_audio.chunks():
                f.write(chunk)

        # Whisper로 STT 처리
        result = model.transcribe('temp_audio.wav')
        student_text = result['text'].strip()

        # 유사도 계산
        target_text = word.text.strip()
        similarity_score = difflib.SequenceMatcher(None, student_text, target_text).ratio() * 100

        return JsonResponse({
            'original_text': target_text,
            'student_text': student_text,
            'score': similarity_score,
            'success': True
        })
