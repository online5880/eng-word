import whisper
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
def recognize_audio(request, question_id):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]

        # Whisper 모델 로드 및 음성 변환
        model = whisper.load_model("small")  # 작은 모델을 사용할 경우 변경
        result = model.transcribe(audio_file)

        return JsonResponse({"transcript": result["text"]})
    return JsonResponse({"error": "Audio file not provided"}, status=400)


def test_mode_view(request):
    # 단순히 템플릿을 렌더링하는 view 함수
    return render(request, "test_mode/test_page.html")
