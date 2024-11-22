import os
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Word, Sentence
import numpy as np
import time
from collections import Counter


# Sigmoid 함수 정의
def sigmoid(x, k=10, threshold=0.6):
    return 1 / (1 + np.exp(-k * (x - threshold)))


# AI 정답률 계산
def calculate_ai_accuracy(student_accuracy, T=0.6, k=10):
    return sigmoid(student_accuracy, k, T)


# AI 응답 속도 계산
def calculate_ai_response_time(student_time, T_min=1.0, T_max=5.0, T_threshold=3.0, k_t=1.5):
    return T_min + (T_max - T_min) * sigmoid(student_time, k_t, T_threshold)


# 문제 학습 화면
def example_sentence_learning(request):
    # 세션에서 선택된 단어 가져오기
    selected_words = request.session.get('selected_words', None)
    if not selected_words:
        return JsonResponse({"error": "No words selected for learning."}, status=400)

    # 게임 상태 초기화 또는 세션에서 가져오기
    game_state = request.session.get('game_state', {
        "student_accuracy": 0.6,
        "current_question": 0,
        "num_questions": len(selected_words),
        "student_scores": [],
        "ai_scores": [],
        "student_response_times": [],
        "ai_response_times": [],
        "student_responses": [],
    })

    # 문제를 모두 푼 경우 결과 페이지로 이동
    if game_state["current_question"] >= game_state["num_questions"]:
        return redirect("sent_result")

    # 현재 단어 및 문장 가져오기
    current_word_data = selected_words[game_state["current_question"]]
    current_word = current_word_data['word']  # 단어
    sentence_data = Sentence.objects.filter(word__word=current_word).first()

    if not sentence_data:
        return JsonResponse({"error": f"No sentences found for word: {current_word}"}, status=400)

    blank_word = "_" * len(current_word)  # 단어 길이만큼 빈칸 생성
    sentence_with_blank = sentence_data.sentence.replace(current_word, blank_word)

    # 문제 데이터를 템플릿으로 전달
    context = {
        "sentence": sentence_with_blank,
        "meaning": sentence_data.sentence_meaning,
        "word": current_word,
        "current_question": game_state["current_question"] + 1,
        "total_questions": game_state["num_questions"],
        "student_accuracy": game_state["student_accuracy"],
    }

    return render(request, "sent_mode/sent_practice.html", context)



# 학습 결과 화면
def sent_result(request):
    game_state = request.session.get('game_state')
    if not game_state:
        return redirect("sent_practice")

    word_frequencies = Counter(game_state["student_responses"])
    final_student_accuracy = game_state["student_accuracy"]
    final_ai_accuracy = calculate_ai_accuracy(final_student_accuracy)

    context = {
        "game_state": game_state,
        "word_frequencies": word_frequencies,
        "final_student_accuracy": final_student_accuracy,
        "final_ai_accuracy": final_ai_accuracy,
    }
    return render(request, "sent_mode/sent_result.html", context)



# 음성 파일 처리
@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            audio_file = request.FILES["audio"]
            current_word = request.POST.get("word", "unknown").strip().lower()
            user_id = request.user.id if request.user.is_authenticated else "anonymous"

            # 녹음 파일 저장 경로
            save_path = f"audio_files/students/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 저장
            file_name = f"{current_word}.wav"
            file_path = os.path.join(save_path, file_name)
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            student_audio_path = default_storage.save(file_path, ContentFile(audio_file.read()))

            # 정답 판단 로직 (STT 결과 활용)
            # 현재 테스트를 위해 단순히 STT 결과를 current_word로 설정
            recognized_word = current_word  # STT 결과로 대체 필요

            # 정답 여부 판단
            is_correct = recognized_word == current_word

            # 세션에서 게임 상태 가져오기 및 업데이트
            game_state = request.session.get('game_state', {})
            current_index = game_state.get("current_question", 0)
            student_accuracy = game_state.get("student_accuracy", 0.6)

            # 학생 정답률 업데이트
            new_student_accuracy = (
                (student_accuracy * current_index + (1 if is_correct else 0)) /
                (current_index + 1)
            )
            game_state["student_accuracy"] = new_student_accuracy

            # AI 정답률 및 응답 시간 계산
            ai_accuracy = calculate_ai_accuracy(new_student_accuracy)
            ai_correct = np.random.rand() < ai_accuracy
            student_time = float(request.POST.get("response_time", 3.0))  # 응답 시간 전달
            ai_response_time = calculate_ai_response_time(student_time)

            # 게임 상태 업데이트
            game_state["student_scores"].append(10 if is_correct else 0)
            game_state["ai_scores"].append(10 if ai_correct else 0)
            game_state["student_responses"].append(recognized_word)
            game_state["ai_response_times"].append(ai_response_time)
            game_state["current_question"] += 1
            request.session['game_state'] = game_state

            # 모든 문제를 풀었는지 확인
            is_last_question = game_state["current_question"] >= game_state["num_questions"]

            return JsonResponse({
                "status": "success",
                "is_correct": is_correct,
                "correct_word": current_word,
                "recognized_word": recognized_word,
                "student_accuracy": new_student_accuracy,
                "ai_accuracy": ai_accuracy,
                "ai_response_time": ai_response_time,
                "message": "Answer checked successfully.",
                "next_question_available": not is_last_question,
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

