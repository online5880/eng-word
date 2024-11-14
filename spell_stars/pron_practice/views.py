import os
import librosa
import numpy as np
from scipy.spatial.distance import cosine
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Word
import random
import warnings
import whisper
from utils.PronunciationChecker.manage import process_audio_files
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

warnings.filterwarnings("ignore", category=FutureWarning)

# Whisper 모델 로드 (small 모델 사용)
model = whisper.load_model("small")


# 발음 연습 페이지를 렌더링하는 뷰
def pronunciation_practice_view(request):
    random_word = Word.objects.values('word', 'meanings').order_by("?").first()

    if random_word:
        request.session['target_word'] = random_word['word']
        return render(
            request, "pron_practice/pron_practice.html", {"word": random_word['word'],  'MEDIA_URL': settings.MEDIA_URL}
        )
    else:
        return JsonResponse({"error": "No words available in the database."}, status=404)

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        try:
            user_id = request.user.id
            word = request.POST.get('word')
            
            if not word:
                return JsonResponse({'status': 'error', 'message': 'Word is required'}, status=400)
            
            # 저장 경로 설정
            save_path = f'pron_pc/user_{user_id}/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)
            
            # 파일 이름 설정
            file_name = f"{word}_student.wav"
            file_path = os.path.join(save_path, file_name)
            
            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            # 새 파일 저장
            full_path = default_storage.save(file_path, ContentFile(request.FILES['audio'].read()))
            
            # 절대 경로로 변환
            native_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio_files/native/', f"{word}.wav")
            full_student_audio_path = os.path.join(settings.MEDIA_ROOT, file_path)

            print("Native audio path:", native_audio_path)  # 디버깅용
            print("Student audio path:", full_student_audio_path)  # 디버깅용
            
            # process_audio_files 호출
            result = process_audio_files(native_audio_path, full_student_audio_path, word)
            print(result)  # 결과 출력
            
            return JsonResponse({
                'status': 'success', 
                'file_path': full_student_audio_path,
                'message': '음성 파일이 성공적으로 저장되었습니다.'
            })
              
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def evaluate_pronunciation(request):
    try:
        if request.method == "POST":
            user_id = request.user.id

            # 세션에서 단어 가져오기
            target_word = request.session.get('target_word')
            if not target_word:
                return JsonResponse({"error": "No target word found in session."}, status=404)

            # 업로드된 파일 경로
            file_path = f'pron_pc/students/user_{user_id}/{target_word}_student.wav'
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # 파일이 존재하지 않으면 오류 반환
            if not os.path.exists(full_path):
                return JsonResponse({"error": f"Audio file for {target_word} not found."}, status=404)

            # 원어민 발음 파일 경로 설정
            native_file_path = os.path.join(settings.MEDIA_ROOT, "audio_files", "native", f"{target_word}.wav")

            if not os.path.exists(native_file_path):
                return JsonResponse({"error": f"Native audio file for {target_word} not found."}, status=404)

            # 발음 비교 수행
            result = process_audio_files(native_file_path, full_path, target_word)

            return JsonResponse({
                "status": "success",
                "score": result['score'],
                "feedback": result['feedback'],
                "target_word": target_word,
            })

        return JsonResponse({"error": "Invalid request"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)



# 다음 단어로 이동하는 뷰
def next_word(request):
    try:
        # 새로운 단어를 임의로 선택
        next_word = Word.objects.order_by('?').first()  # 랜덤으로 단어 가져오기
        
        if next_word:
            return JsonResponse({'success': True, 'nextWord': next_word.text})  # 단어 텍스트 반환
        else:
            return JsonResponse({'success': False, 'message': '단어가 없습니다.'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})