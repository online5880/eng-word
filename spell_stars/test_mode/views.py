from django.shortcuts import render
from django.http import JsonResponse
import whisper
from django.views.decorators.csrf import csrf_exempt
import random


# 음성 인식 API를 통해 음성 파일을 텍스트로 변환
@csrf_exempt
def recognize_audio(request, question_id):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]

        # Whisper 모델 로드 및 음성 변환
        model = whisper.load_model("small")  # 작은 모델을 사용할 경우 변경
        result = model.transcribe(audio_file)

        return JsonResponse({"transcript": result["text"]})
    return JsonResponse({"error": "Audio file not provided"}, status=400)


# 시험 문제 페이지
def test_mode_view(request):
    # 예시 문장과 정답 단어 하드코딩
    sentences = [
        {"sentence": "I can't find my eraser.", "word": "eraser"},
        {"sentence": "She is reading a book.", "word": "book"},
        {"sentence": "My favorite fruit is apple.", "word": "apple"},
    ]

    # 랜덤으로 문장 하나 선택
    selected = random.choice(sentences)
    sentence = selected["sentence"]
    target_word = selected["word"]

    # 예문에서 타겟 단어를 '_____'로 바꿔 빈칸을 생성
    problem_sentence = sentence.replace(target_word, "_____")

    return render(
        request,
        "test_mode/test_page.html",
        {"sentence": problem_sentence, "answer": target_word},
    )
