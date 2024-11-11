import json
import os
import random
import re
from django.shortcuts import render
from django.http import JsonResponse
import whisper
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


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
    # JSON 파일 경로 설정
    parent_dir = os.path.dirname(settings.BASE_DIR)  # BASE_DIR의 부모 디렉토리
    words_file_path = os.path.join(
        parent_dir, "utils", "json_words", "combined", "combined_words.json"
    )
    examples_file_path = os.path.join(
        parent_dir, "utils", "json_words", "combined", "combined_examples.json"
    )

    # JSON 파일 읽기
    try:
        with open(words_file_path, "r", encoding="utf-8") as f:
            words_data = json.load(f)

        with open(examples_file_path, "r", encoding="utf-8") as f:
            examples_data = json.load(f)
    except FileNotFoundError as e:
        return JsonResponse({"error": f"File not found: {str(e)}"}, status=404)

    # 랜덤으로 단어 하나 선택
    selected_word = random.choice(words_data)

    # 선택된 단어가 포함된 예문 찾기
    matching_examples = [
        example for example in examples_data if selected_word in example
    ]

    if not matching_examples:
        return JsonResponse(
            {"error": f"Word '{selected_word}' not found in any examples."}, status=404
        )

    # 예문에서 랜덤으로 하나 선택
    selected_example = random.choice(matching_examples)

    # 선택된 예문에서 단어를 빈칸으로 교체
    problem_sentence = re.sub(
        r"\b" + re.escape(selected_word) + r"\b", "_____", selected_example
    )

    # 선택된 단어와 예문, 빈칸 처리된 예문을 디버깅용으로 확인
    print(f"Selected Word: {selected_word}")
    print(f"Original Example: {selected_example}")
    print(f"Problem Sentence: {problem_sentence}")

    # 빈칸으로 대체된 예문과 정답 단어를 템플릿에 전달
    return render(
        request,
        "test_mode/test_page.html",
        {"sentence": problem_sentence, "answer": selected_word},
    )
