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
    print(f"Calculating AI accuracy with student_accuracy: {student_accuracy}, T: {T}, k: {k}")
    return sigmoid(student_accuracy, k, T)


# AI 응답 속도 계산
def calculate_ai_response_time(student_time, T_min=1.0, T_max=5.0, T_threshold=3.0, k_t=1.5):
    print(f"Calculating AI response time with student_time: {student_time}, T_min: {T_min}, T_max: {T_max}")
    return T_min + (T_max - T_min) * sigmoid(student_time, k_t, T_threshold)


# 문제 학습 화면
def example_sentence_learning(request):
    print("Initializing game state with pre-selected words...")
    
    # `selected_words`를 요청에서 가져오기
    selected_words = request.session.get('selected_words', [])
    
    if not selected_words:
        # 선택된 단어가 없으면 초기화
        selected_words = [
            {'word': 'apple', 'meanings': '사과', 'category': 'fruit', 'examples': 'An apple a day keeps the doctor away.'},
            {'word': 'banana', 'meanings': '바나나', 'category': 'fruit', 'examples': 'Bananas are high in potassium.'},
        ]
        request.session['selected_words'] = selected_words

    request.session['game_state'] = {
        "student_accuracy": 0.0,           # 초기 학생 정답률
        "current_question": 0,            # 현재 문제 인덱스
        "num_questions": len(selected_words),  # 총 문제 수
        "student_responses": [],          # 학생 응답 기록
    }

    print(f"Selected words: {selected_words}")
    print("Game state initialized.")
    return redirect("sent_practice")


def sent_practice(request):
    game_state = request.session.get('game_state')
    selected_words = request.session.get('selected_words')

    if not game_state or not selected_words:
        return redirect("example_sentence_learning")

    if game_state["current_question"] >= game_state["num_questions"]:
        return redirect("sent_result")

    # 현재 문제 데이터 가져오기
    try:
        current_word_data = selected_words[game_state["current_question"]]
    except (IndexError, KeyError):
        print(f"Error: Invalid question index {game_state['current_question']}")
        return redirect("sent_result")

    current_word = current_word_data['word']
    sentence_data = Sentence.objects.filter(word__word=current_word).first()

    if not sentence_data:
        sentence_data = Sentence(
            sentence=f"This is a sentence for the word '{current_word}'.",
            sentence_meaning=f"Meaning for '{current_word}'"
        )

    blank_word = "_" * len(current_word)
    sentence_with_blank = sentence_data.sentence.replace(current_word, blank_word)

    context = {
        "sentence": sentence_with_blank,
        "meaning": sentence_data.sentence_meaning,
        "word": current_word,
        "current_question": game_state["current_question"] + 1,
        "total_questions": game_state["num_questions"],
        "student_accuracy": game_state["student_accuracy"],
    }

    print(f"Rendering question {game_state['current_question'] + 1}/{game_state['num_questions']}")
    return render(request, "sent_mode/sent_practice.html", context)



# 학습 결과 화면
def sent_result(request):
    game_state = request.session.get('game_state')
    if not game_state:
        return redirect("sent_practice")

    student_responses = game_state.get("student_responses", [])
    word_frequencies = Counter(student_responses) if student_responses else Counter()
    print(f"Word frequencies: {word_frequencies}")

    # 평균 응답 시간 계산
    student_times = game_state.get("student_times", [])
    ai_times = game_state.get("ai_times", [])
    avg_student_time = sum(student_times) / len(student_times) if student_times else 0
    avg_ai_time = sum(ai_times) / len(ai_times) if ai_times else 0

    total_questions = game_state.get("num_questions", 0)
    correct_answers = sum(1 for response in student_responses if response)
    final_student_accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    final_ai_accuracy = calculate_ai_accuracy(correct_answers / total_questions) * 100 if total_questions > 0 else 0
    score_difference = abs(final_student_accuracy - final_ai_accuracy)
    student_times = game_state.get('student_times', [])
    ai_times = game_state.get('ai_times', [])

    unique_words_used = len(word_frequencies)
    total_words = len(request.session.get('selected_words', []))
    learning_performance_message = (
        "모든 단어를 고르게 학습했습니다! 잘했습니다!"
        if unique_words_used == total_words
        else "특정 단어에 편중되었습니다. 더 다양한 단어를 학습해보세요!"
    )

    context = {
        "student_times": student_times,
        "ai_times": ai_times,
        "final_student_accuracy": final_student_accuracy,
        "final_ai_accuracy": final_ai_accuracy,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "score_difference": score_difference,
        "word_frequencies": dict(word_frequencies),  # `.items()`를 템플릿에서 사용하도록 변환
        "unique_words_used": unique_words_used,
        "total_words": total_words,
        "learning_performance_message": learning_performance_message,
        "avg_student_time": avg_student_time,  # 평균 학생 응답 시간
        "avg_ai_time": avg_ai_time,           # 평균 AI 응답 시간
    }

    print("Resetting session data...")
    
    response = render(request, "sent_mode/sent_result.html", context)
    request.session.flush()
    return response



# 음성 파일 처리
@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        try:
            print("Audio upload request received.")  # 요청 수신 확인
            audio_file = request.FILES['audio']
            print(f"Audio file received: {audio_file.name}")  # 파일 이름 확인
            current_word = request.POST.get('word', 'unknown').strip().lower()
            print(f"Current word: {current_word}")  # 단어 정보 확인

            # 파일 저장
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            save_path = f'audio_files/students/user_{user_id}/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)
            file_name = f'{current_word}_st.wav'
            file_path = os.path.join(save_path, file_name)
            print(f"File will be saved to: {file_path}")  # 저장 경로 확인

            if default_storage.exists(file_path):
                print(f"File already exists. Deleting: {file_path}")
                default_storage.delete(file_path)

            saved_path = default_storage.save(file_path, ContentFile(audio_file.read()))
            print(f"File saved at: {saved_path}")  # 저장 확인

            # STT 결과 처리 (임시로 현재 단어 사용)
            recognized_word = current_word  # 실제 STT 결과를 추가
            is_correct = (recognized_word == current_word)  # 정답 여부 확인

            # 학생 응답 시간 가져오기
            student_time = float(request.POST.get('student_time', 3.0))  # 기본값 3초


            # 게임 상태 업데이트
            game_state = request.session.get('game_state', {})
            
            game_state['ai_times'] = game_state.get('ai_times', [])
            game_state['student_responses'] = game_state.get('student_responses', [])
            current_index = game_state.get('current_question', 0)
            student_accuracy = game_state.get('student_accuracy', 0.0)

            # 새로운 정답률 계산
            new_accuracy = ((student_accuracy * current_index) + int(is_correct)) / (current_index + 1)
            game_state['student_accuracy'] = new_accuracy
            game_state['student_responses'].append(recognized_word)
            
            # 학생 응답 시간 저장
            if 'student_times' not in game_state:
                game_state['student_times'] = []
            game_state['student_times'].append(student_time)
            # AI 정답 및 반응 시간 계산
            ai_accuracy = calculate_ai_accuracy(new_accuracy)
            ai_correct = bool(random.random() < ai_accuracy)  # numpy.bool_ -> Python bool 변환
            student_time = float(request.POST.get('student_time', 3.0))
            ai_response_time = calculate_ai_response_time(student_time)

            print("Game state updated:", game_state)

            # AI 응답 시간 기록 추가
            game_state['ai_times'].append(ai_response_time)

            game_state['current_question'] += 1
            request.session['game_state'] = game_state

            # 마지막 문제인지 확인
            if game_state['current_question'] >= game_state['num_questions']:
                print("All questions answered. Redirecting to results...")
                return JsonResponse({'redirect': '/sent/result/'})

            # JSON 응답 반환
            return JsonResponse({
                'is_correct': is_correct,
                'student_time': student_time,
                'ai_correct': ai_correct,
                'student_accuracy': new_accuracy,
                'ai_accuracy': ai_accuracy,
                'ai_response_time': ai_response_time
            })

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    print("Invalid request received.")
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def next_question(request):
    # 세션 데이터 가져오기
    game_state = request.session.get('game_state')
    selected_words = request.session.get('selected_words')

    # 세션 상태 검증
    if not game_state or not selected_words:
        return JsonResponse({"error": "세션 데이터가 손상되었습니다. 다시 시도해주세요."}, status=400)

    # 현재 문제 인덱스 가져오기
    current_question = game_state.get("current_question", 0)
    total_questions = len(selected_words)

    if current_question >= total_questions:
        return JsonResponse({"error": "퀴즈가 완료되었습니다."}, status=400)

    try:
        # 다음 단어 데이터 가져오기
        next_word_data = selected_words[current_question]
        next_sentence = Sentence.objects.filter(word__word=next_word_data['word']).first()

        # 예문이 없을 경우 기본 데이터 생성
        if not next_sentence:
            print(f"No sentence found for word: {next_word_data['word']}, generating default.")
            next_sentence = Sentence(
                sentence=f"This is a sentence for the word '{next_word_data['word']}'.",
                sentence_meaning=f"Meaning for '{next_word_data['word']}'"
            )

        # 문제 인덱스 증가 및 세션 업데이트
        game_state["current_question"] += 1
        request.session["game_state"] = game_state

        # JSON 응답 반환
        return JsonResponse({
            "sentence": next_sentence.sentence.replace(next_word_data['word'], "_" * len(next_word_data['word'])),
            "meaning": next_sentence.sentence_meaning,
            "word": next_word_data['word'],
            "current_question": game_state["current_question"],
            "total_questions": total_questions,
        })

    except IndexError:
        print(f"IndexError: current_question ({current_question}) is out of range.")
        return JsonResponse({"error": "더 이상 문제가 없습니다."}, status=400)

    except Exception as e:
        print(f"Unexpected error in next_question: {e}")
        return JsonResponse({"error": f"오류 발생: {str(e)}"}, status=500)

