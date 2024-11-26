import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from vocab_mode.models import Word
import warnings
from django.apps import apps
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from accounts.views import start_learning_session

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = apps.get_app_config("spell_stars").whisper_model
processor = apps.get_app_config('spell_stars').whisper_processor


def pronunciation_practice_view(request):
    # 새로운 단어 선택
    random_word = (
        Word.objects.values("word", "meanings", "file_path").order_by("?").first()
    )

    if random_word:
        # 공백을 _로 변경
        word_with_underscores = random_word["word"].replace(" ", "_")
        
        # 수정된 단어를 세션에 저장
        request.session["target_word"] = word_with_underscores
        
        # 학습 시작 로그 생성
        start_learning_session(request, learning_mode=3)  # pron_practice 2번

        return render(
            request,
            "pron_practice/pron_practice.html",
            {
                "word": word_with_underscores,  # 수정된 단어를 전달
                "meanings": random_word["meanings"],
                "file_path": random_word["file_path"],
                "pronunciation_score": 0,
                "MEDIA_URL": settings.MEDIA_URL,
            },
        )
    else:
        return JsonResponse(
            {"error": "No words available in the database."}, status=404
        )


@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            audio_file = request.FILES["audio"]
            current_word = request.POST.get("word", "unknown")
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            username = request.user.username if request.user.is_authenticated else "anonymous"
            
            # 저장 경로 설정
            save_path = f"pron_pc/students/user_{user_id}/"
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

            result = process_audio_files(native_audio_path,student_audio_path,current_word,user_id,username)
            score = round(result["overall_score"], 2)

            return JsonResponse({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path,
                "result":result,
                "score": score
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


def next_word(request):
    try:
        # 새로운 단어를 임의로 선택
        next_word = Word.objects.order_by("?").first()  # 랜덤으로 단어 가져오기
        print(next_word)
        
        if next_word:
            # 단어 중간에 공백이 있으면 언더바로 대체
            word_with_underscores = next_word.word.replace(" ", "_")
            
            # 세션에서 발음 점수 초기화
            request.session["pronunciation_score"] = 0  # 점수 초기화

            return JsonResponse(
                {
                    "success": True,
                    "nextWord": word_with_underscores,  # 공백을 언더바로 변환한 단어 반환
                    "nextMeanings": next_word.meanings,  # 단어 뜻 텍스트 반환
                    "nextFilePath": next_word.file_path,  # 오디오 경로 반환
                }
            )  # 단어 텍스트와 오디오 경로 반환
        else:
            return JsonResponse({"success": False, "message": "단어가 없습니다."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


def exit_practice(request):
    return redirect("main")  # 메인 페이지로 리다이렉트 (URL 패턴에 맞게 변경)
