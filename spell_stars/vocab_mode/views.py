import os
import random
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.PronunciationChecker.manage import process_audio_files
from .models import Word
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .serializers import AudioUploadSerializer, WordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.views import start_learning_session, end_learning_session
from rest_framework.permissions import AllowAny

import random
from django.conf import settings
from django.shortcuts import render
from .models import Word

def display_vocabulary_book_random_category(request):
    # 모든 카테고리 가져오기 (중복 제거)
    categories = list(Word.objects.values_list('category', flat=True).distinct())
    
    selected_words = []
    selected_categories = []
    
    # 남은 카테고리 중 랜덤 선택
    if categories:
        random_category = random.choice(categories)
        category_words = list(Word.objects.filter(category=random_category))
        
        # 카테고리 내 단어가 5개 이하일 경우 그대로 선택
        if len(category_words) <= 5:
            selected_words.extend(category_words)
            selected_categories.append(random_category)
        else:
            # 카테고리 내에서 랜덤으로 5개만 선택
            selected_words.extend(random.sample(category_words, 5))
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
        context = {"words": selected_words, "MEDIA_URL": settings.MEDIA_URL}
    else:
        all_words = list(Word.objects.all())
        random_words = random.sample(all_words, min(len(all_words), 15))
        context = {"words": random_words, "MEDIA_URL": settings.MEDIA_URL}
        
    # 학습 시작 로그 생성
    start_learning_session(request, learning_mode=1)
    return render(request, "vocab_mode/vocab.html", context)


@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            audio_file = request.FILES["audio"]
            current_word = request.POST.get("word", "unknown")
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            username = request.user.name if request.user.is_authenticated else "anonymous"
            print("유저이름 :  ",username)
            print("유저 id :  ",user_id)
            
            # 저장 경로 설정
            save_path = f"audio_files/students/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{current_word}_st.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(audio_file.read())
            )
            
            native_audio_path = os.path.join(
                settings.MEDIA_ROOT, "audio_files/native/", f"{current_word}.wav"
            )
            student_audio_path = os.path.join(
                settings.MEDIA_ROOT, save_path, f"{current_word}_st.wav"
            )
            
            print(student_audio_path)
            print(native_audio_path)
            # test_path = "C:/Users/user/Desktop/eng-word/media/audio_files/native/actually.wav"
            result = process_audio_files(native_audio_path,student_audio_path,current_word,user_id,username)
            # result = process_audio_files(native_audio_path,student_audio_path,current_word,user_id)
            return JsonResponse({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path,
                "result": result
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

def sentence_mode(request):
    end_learning_session(request)
    # 세션에서 선택된 단어들 가져오기
    selected_words = request.session.get('selected_words', [])
    
    context = {
        "words": selected_words,
        "MEDIA_URL": settings.MEDIA_URL
    }
    
    # 학습 시작 로그 생성 (예문 모드는 learning_mode=1로 설정)
    start_learning_session(request, learning_mode=1)
    return render(request, "sent_mode", context)

### API Views ###

class WordPagination(PageNumberPagination):
    """단어 목록 페이지네이션 설정"""
    page_size = 100  # 페이지당 단어 수

class WordListAPIView(ListAPIView):
    """
    단어 목록을 제공하는 API
    
    Endpoint: GET /api/words/
    Features:
    - 페이지네이션 (100개씩)
    - 검색 기능 (단어, 의미)
    - 카테고리 필터링 (?category=카테고리명)
    """
    permission_classes = [IsAuthenticated]
    queryset = Word.objects.all().order_by("category", "word")
    serializer_class = WordSerializer
    pagination_class = WordPagination
    filter_backends = [SearchFilter]
    search_fields = ["word", "meanings"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        return queryset.filter(category=category) if category else queryset

class CategoryListAPIView(APIView):
    """
    전체 카테고리 목록을 제공하는 API (알파벳 순 정렬)
    
    Endpoint: GET /api/categories/
    Returns: 정렬된 카테고리 이름 목록
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Word.objects.values_list('category', flat=True)\
                       .distinct()\
                       .order_by('category')  # 카테고리명 기준 오름차순 정렬
        return Response(list(categories))

class WordsByCategoryAPIView(APIView):
    """
    특정 카테고리의 단어 목록을 제공하는 API
    
    Endpoint: GET /api/categories/<category_id>/words/
    Returns: 해당 카테고리의 모든 단어 정보
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category_id):
        words = Word.objects.filter(category=category_id).order_by("word")
        if not words.exists():
            return Response(
                {"error": "해당 카테고리를 찾을 수 없습니다"}, 
                status=404
            )
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)


class PronunciationCheckerAPIView(APIView):
    # permission_classes = [AllowAny] # 
    """
    PronunciationCheckerAPIView는 학생의 녹음 파일을 서버에 저장하고,
    원어민 발음과 비교하여 발음 채점 결과를 반환하는 API 뷰입니다.

    주요 동작:
    - 사용자가 업로드한 오디오 파일과 발음 단어를 검증합니다.
    - 파일을 지정된 경로에 저장합니다.
    - 원어민 발음 파일과 학생의 발음 파일을 비교하여 발음 점수를 계산합니다.

    요청:
        POST 요청으로 오디오 파일(`audio`)과 발음 단어(`word`)를 포함해야 합니다.
        사용자가 인증된 경우, 사용자 ID와 이름을 저장합니다.

    응답:
        - 성공 시:
            - status: "success"
            - message: "녹음이 완료되었습니다."
            - file_path: 저장된 파일 경로
            - result: 발음 비교 결과
        - 실패 시:
            - status: "error"
            - message: 오류 메시지

    예외 처리:
    - 데이터 검증 실패 시 400 상태 코드를 반환합니다.
    - 기타 예외 발생 시 500 상태 코드를 반환합니다.

    """
    @swagger_auto_schema(
        operation_description="학생 발음 파일 업로드 및 정답 단어와의 일치 여부 확인",
        manual_parameters=[
            openapi.Parameter(
                name="audio",
                in_=openapi.IN_FORM,
                description="학생의 발음 오디오 파일",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                name="word",
                in_=openapi.IN_FORM,
                description="정답 단어",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                "STT 결과 반환",
                examples={
                    "application/json": {
                        "is_correct": True
                    }
                }
            ),
            400: "잘못된 요청 데이터",
            500: "서버 오류"
        }
    )
    def post(self, request):
        # 데이터 검증
        serializer = AudioUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 요청 데이터 추출
            audio_file = serializer.validated_data['audio']
            current_word = serializer.validated_data['word']
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            username = request.user.username if request.user.is_authenticated else "anonymous"
            
            print("유저 이름:", username)
            print("유저 ID:", user_id)

            # 저장 경로 설정
            save_path = f"audio_files/students/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{current_word}_st.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(file_path, ContentFile(audio_file.read()))

            # Native 및 학생 오디오 경로 생성
            native_audio_path = os.path.join(
                settings.MEDIA_ROOT, "audio_files/native/", f"{current_word}.wav"
            )
            student_audio_path = os.path.join(
                settings.MEDIA_ROOT, save_path, f"{current_word}_st.wav"
            )

            print("학생 오디오 경로:", student_audio_path)
            print("원어민 오디오 경로:", native_audio_path)

            # 오디오 파일 처리 (process_audio_files 함수 호출)
            result = process_audio_files(native_audio_path, student_audio_path, current_word, user_id, username)

            return Response({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path,
                "result": result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)