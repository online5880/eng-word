import os
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from vocab_mode.models import Word
from accounts.models import StudentInfo
import warnings
from django.apps import apps
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Sentence, LearningResult

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = apps.get_app_config("spell_stars").whisper_model


# 예문 학습 페이지 렌더링
from django.shortcuts import redirect, render
from .models import Word, Sentence

# 예문 학습 페이지 렌더링
def example_sentence_learning(request):
    user = request.user
    # 세션에서 선택된 단어들 가져오기
    selected_words = request.session.get('selected_words', None)
    
    selected_words_list = [item['word'] for  item in selected_words]

    # selected_words에서 Word 모델 객체들을 찾아서 필터링
    word_objects = Word.objects.filter(word__in=selected_words_list)
    print("sent words : ",word_objects)

    # 세션에 저장된 단어들에 해당하는 예문들 가져오기
    sentences = Sentence.objects.filter(word__in=word_objects).order_by("?")
    # print("sent sentence : ",sentence)

    # 예문에 단어를 빈칸으로 대체
    blank_sentences = []
    for sentence in sentences:
        # 단어의 길이만큼 언더바 생성
        word_length = len(sentence.word.word)
        blank = "_" * word_length  # 예: "toilet" -> "______"

        # 문장에서 해당 단어를 언더바로 대체
        blank_sentence = sentence.sentence.replace(sentence.word.word, blank)
        blank_sentences.append({
            "sentence": blank_sentence,
            "meaning": sentence.sentence_meaning,
            "word": sentence.word.word
        })

    context = {
        "sentences": blank_sentences,
        "selected_words": selected_words
    }
    
    return render(request, "sent_mode/sent_practice.html", context)

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
            file_name = f"{current_word}.wav"
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
                settings.MEDIA_ROOT, save_path, f"{current_word}.wav"
            )
            
            result = process_audio_files(native_audio_path,native_audio_path,current_word,user_id)
            print(student_audio_path)
            print(native_audio_path)
            # result = process_audio_files(native_audio_path,student_audio_path,current_word,user_id)
            print("결과",result)
            return JsonResponse({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path,
                "result":result,
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


def exit_learning_mode(request):
    # 세션 초기화
    if 'selected_theme' in request.session:
        del request.session['selected_theme']

    # 메인 페이지로 리디렉션
    return redirect('home')  # 홈 페이지로 이동