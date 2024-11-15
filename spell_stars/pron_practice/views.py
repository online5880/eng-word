import os
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from vocab_mode.models import Word
import warnings
from django.apps import apps
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = apps.get_app_config("spell_stars").whisper_model


def pronunciation_practice_view(request):
    # 새로운 단어 선택
    random_word = (
        Word.objects.values("word", "meanings", "file_path").order_by("?").first()
    )

    if random_word:
        request.session["target_word"] = random_word["word"]

        return render(
            request,
            "pron_practice/pron_practice.html",
            {
                "word": random_word["word"],
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
            user_id = request.user.id
            word = request.POST.get("word")

            if not word:
                return JsonResponse(
                    {"status": "error", "message": "Word is required"}, status=400
                )

            # 저장 경로 설정
            save_path = f"pron_pc/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(request.FILES["audio"].read())
            )

            # 절대 경로로 변환
            native_audio_path = os.path.join(
                settings.MEDIA_ROOT, "audio_files/native/", f"{word}.wav"
            )
            full_student_audio_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # 발음 비교 처리
            result = process_audio_files(
                native_audio_path, full_student_audio_path, word
            )

            if result["status"] == "error":
                return JsonResponse(result)

            # 발음 점수 저장
            pronunciation_score = result["result"]["overall_score"]
            request.session["pronunciation_score"] = pronunciation_score

            return JsonResponse(
                {
                    "status": "success",
                    "file_path": full_student_audio_path,
                    "score": round(pronunciation_score, 1),  # 소수점 한자리까지 반환
                    "message": "음성 파일이 성공적으로 저장되고 발음 평가가 완료되었습니다.",
                }
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


# 다음 단어로 이동하는 뷰
def next_word(request):
    try:
        # 새로운 단어를 임의로 선택
        next_word = Word.objects.order_by("?").first()  # 랜덤으로 단어 가져오기
        print(next_word)
        if next_word:
            # 세션에서 발음 점수 초기화
            request.session["pronunciation_score"] = 0  # 점수 초기화

            return JsonResponse(
                {
                    "success": True,
                    "nextWord": next_word.word,  # 단어 텍스트 반환
                    "nextMeanings": next_word.meanings,  # 단어 뜻 텍스트 반환
                    "nextFilePath": next_word.file_path,  # 오디오 경로 반환
                }
            )  # 단어 텍스트와 오디오 경로 반환
        else:
            return JsonResponse({"success": False, "message": "단어가 없습니다."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


from django.shortcuts import redirect


def exit_practice(request):
    # 발음 연습에 관련된 데이터 처리(필요한 경우)
    return redirect("main")  # 메인 페이지로 리다이렉트 (URL 패턴에 맞게 변경)
