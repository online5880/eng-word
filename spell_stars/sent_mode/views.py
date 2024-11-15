from django.http import JsonResponse
from django.shortcuts import render
from .models import Sentence, LearningResult
from vocab_mode.models import Word
from accounts.models import User
from django.apps import apps

# Whisper 모델 초기화 (whisper-small)
model = apps.get_app_config('spell_stars').whisper_model


# 예문 학습 페이지 렌더링
def example_sentence_learning(request):
    # 사용자가 이미 학습한 테마 중 랜덤으로 하나 선택
    user = request.user
    selected_theme = user.selected_theme  # 사용자가 선택한 테마 (랜덤 선택 로직 필요)

    # 예문 테이블에서 해당 테마의 예문 랜덤으로 가져오기
    sentences = Sentence.objects.filter(theme_id=selected_theme.id).order_by("?")[:5]

    # 예문 정보 준비 (빈칸으로 대체된 예문과 그 의미 포함)
    context = {
        "sentences": sentences,
    }

    return render(request, "sent_mode/sent_practice.html", context)


# 음성 인식 처리 (Whisper 사용)
def recognize_audio(request, sentence_id):
    if request.method == "POST":
        audio_file = request.FILES.get("audio_file")  # 사용자가 제출한 오디오 파일
        sentence = Sentence.objects.get(id=sentence_id)  # 해당 예문 찾기
        word = sentence.word.word  # 예문에서 해당 단어 (정답)

        # 음성 파일 저장 (임시 저장)
        with open("audio_temp.wav", "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Whisper 모델로 음성 파일 텍스트 변환
        result = model.transcribe("audio_temp.wav")
        transcript = result["text"]  # 음성 인식 결과

        # 음성 인식 결과와 정답 비교
        is_correct = transcript.lower() == word.lower()

        # 정오답 결과 처리
        if is_correct:
            feedback = {
                "error": False,
                "transcript": transcript,
                "audio_url": "/media/audio_files/success.mp3",  # 성공시 반환할 오디오 파일
            }
        else:
            feedback = {
                "error": False,
                "transcript": transcript,
                "audio_url": "/media/audio_files/fail.mp3",  # 실패시 반환할 오디오 파일
            }

        # 학습 결과 저장 (결과 테이블에 저장)
        # 사용자 ID, 예문 ID, 정오답, 단어 사용 빈도 점수 등을 기반으로 결과 기록
        result_data = {
            "user_id": request.user.id,
            "sentence_id": sentence.id,
            "is_correct": is_correct,
            "score": calculate_score(
                is_correct, word, transcript
            ),  # 사용자 정의 점수 계산 함수
        }

        # 학습 결과 테이블에 저장
        LearningResult.objects.create(**result_data)

        return JsonResponse(feedback)

    return JsonResponse({"error": "Invalid request"}, status=400)
