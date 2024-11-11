from django.shortcuts import render
from .models import Word, Example


def example_learning(request):
    # 예시로 단어와 예문을 하나씩 가져옵니다.
    word = Word.objects.first()  # 임시로 첫 번째 단어를 가져옴
    examples = Example.objects.filter(word=word)  # 해당 단어의 예문을 가져옴

    return render(
        request, "example_learning.html", {"word": word, "examples": examples}
    )
