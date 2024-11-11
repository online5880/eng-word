from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Word
from django.contrib.sessions.models import Session


def word_learning_view(request):
    # 현재 단어의 인덱스를 세션에 저장하고 불러오기
    current_word_index = request.session.get("current_word_index", 0)
    words = Word.objects.all()

    # 모든 단어를 학습했으면 예문 학습 모드로 이동
    if current_word_index >= len(words):
        return redirect("sent_mode")  # 예문 학습 모드로 리다이렉트

    word = words[current_word_index]

    if request.method == "POST":
        pronunciation_level = int(request.POST.get("pronunciation_level", 0))

        # 발음 수준이 기준을 넘으면 다음 단어로 이동
        if pronunciation_level >= 80:
            current_word_index += 1
            request.session["current_word_index"] = (
                current_word_index  # 세션에 현재 단어 인덱스 저장
            )

        # 모든 단어 학습이 끝났으면 예문 학습 모드로 리다이렉트
        if current_word_index >= len(words):
            return JsonResponse({"all_words_learned": True})

        # 아직 단어가 남아 있으면 현재 단어 반환
        return JsonResponse({"score": pronunciation_level, "all_words_learned": False})

    return render(request, "vocab_mode/word_learning.html", {"word": word})
