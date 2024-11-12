import json
import os
import random
import re
from django.shortcuts import render
from django.http import JsonResponse
import whisper
from django.conf import settings
from django.core.files.storage import default_storage
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
model = whisper.load_model("small")


def test_mode_view(request):
    print("test_mode_view called")
    parent_dir = os.path.dirname(settings.BASE_DIR)
    words_file_path = os.path.join(
        parent_dir, "utils", "json_words", "combined", "combined_words.json"
    )
    examples_file_path = os.path.join(
        parent_dir, "utils", "json_words", "combined", "combined_examples.json"
    )

    try:
        with open(words_file_path, "r", encoding="utf-8") as f:
            words_data = json.load(f)
        with open(examples_file_path, "r", encoding="utf-8") as f:
            examples_data = json.load(f)
        print(f"Loaded words data and examples data")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {str(e)}")
        return JsonResponse({"error": f"File not found: {str(e)}"}, status=404)

    selected_word = random.choice(words_data)
    matching_examples = [
        example for example in examples_data if selected_word in example
    ]
    print(f"Selected word: {selected_word}")

    if not matching_examples:
        print(f"No examples found for the selected word '{selected_word}'")
        return JsonResponse(
            {"error": f"Word '{selected_word}' not found in any examples."}, status=404
        )

    # Find the index of the selected example in the examples_data list
    selected_example = random.choice(matching_examples)
    question_id = examples_data.index(selected_example)  # Get the index of the example
    print(f"Selected example: {selected_example}, Question ID: {question_id}")

    problem_sentence = re.sub(
        r"\b" + re.escape(selected_word) + r"\b", "_____", selected_example
    )
    print(f"Problem sentence: {problem_sentence}")

    return render(
        request,
        "test_mode/test_page.html",
        {
            "sentence": problem_sentence,
            "answer": selected_word,
            "question_id": question_id,
        },
    )


def recognize_audio(request, question_id):
    print(f"recognize_audio called for question_id: {question_id}")
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        print(f"Received file: {audio_file.name}, Size: {audio_file.size} bytes")

        file_name = f"audio_{question_id}.wav"
        file_path = os.path.join(settings.MEDIA_ROOT, "test_mode", file_name)
        print(f"Saving audio file to {file_path}")

        try:
            with default_storage.open(file_path, "wb") as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            print(f"Audio file saved at {file_path}")
        except Exception as e:
            print(f"Failed to save file: {str(e)}")
            return JsonResponse({"error": f"Failed to save file: {str(e)}"}, status=500)

        try:
            result = model.transcribe(file_path, language="ko")
            transcript = result["text"]
            print(f"Transcript from Whisper: {transcript}")

            return JsonResponse({"transcript": transcript})

        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
            return JsonResponse(
                {"error": f"Failed to transcribe audio: {str(e)}"}, status=500
            )

    print("No audio file received in request")
    return JsonResponse({"error": "No audio file received"}, status=400)