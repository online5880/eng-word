import os
import random
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# from utils.PronunciationChecker.manage import process_audio_files
from .models import Word
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from .serializers import WordSerializer
from rest_framework import filters

def display_vocabulary_book_random_category(request):
    # 모든 카테고리 가져오기 (중복 제거)
    categories = list(Word.objects.values_list('category', flat=True).distinct())
    
    selected_words = []
    selected_categories = []
    
    # 남은 카테고리 중 랜덤 선택
    if categories:
        random_category = random.choice(categories)
        category_words = list(Word.objects.filter(category=random_category))
        
        selected_words.extend(category_words)
        selected_categories.append(random_category)
        
        # 만약 첫 카테고리의 단어가 15개 미만이면 추가 카테고리 선택
        if len(selected_words) < 15:
            categories.remove(random_category)  # 선택된 카테고리는 제거
            
            # 추가 카테고리 선택 로직
            while categories and len(selected_words) < 15:
                random_category = random.choice(categories)
                categories.remove(random_category)
                
                category_words = list(Word.objects.filter(category=random_category))
                if len(selected_words) + len(category_words) > 15:
                    break
                    
                selected_words.extend(category_words)
                selected_categories.append(random_category)
    
    # 카테고리별 단어 수 계산
    category_counts = {
        category: Word.objects.filter(category=category).count()
        for category in selected_categories
    }
    
    # 선택된 단어들을 세션에 저장
    request.session['selected_words'] = [
        {
            'word': word.word,
            'meanings': word.meanings,
            'category': word.category,
            'examples': word.examples,
            'file_path': word.file_path
        }
        for word in selected_words
    ]
    
    context = {
        "words": selected_words,
        "MEDIA_URL": settings.MEDIA_URL,
        "category_counts": category_counts,
        "selected_categories": selected_categories
    }
    return render(request, "vocab_mode/vocab_random_category.html", context)


def display_vocabulary_book(request):
    # 세션에서 선택된 단어들 가져오기
    selected_words = request.session.get('selected_words')
    
    if selected_words:
        # 세션에 저장된 단어들 사용
        context = {"words": selected_words, "MEDIA_URL": settings.MEDIA_URL}
        # 세션 데이터 삭제
        del request.session['selected_words']
    else:
        # 기존 랜덤 로직 사용
        all_words = list(Word.objects.all())
        random_words = random.sample(all_words, min(len(all_words), 15))
        context = {"words": random_words, "MEDIA_URL": settings.MEDIA_URL}
    
    return render(request, "vocab_mode/vocab.html", context)


@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            audio_file = request.FILES["audio"]
            current_word = request.POST.get("word", "unknown")
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            
            # 저장 경로 설정
            save_path = f"audio_files/students/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{current_word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(audio_file.read())
            )
            
            return JsonResponse({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "잘못된 요청입니다."
    }, status=400)


### API
# 단어 목록 GET API
class WordPagination(PageNumberPagination):
    page_size = 100


class WordListAPIView(ListAPIView):
    queryset = Word.objects.all().order_by("category", "word")
    serializer_class = WordSerializer
    pagination_class = WordPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["word", "meanings"]  # 정확히 일치하는 단어로 검색