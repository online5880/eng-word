from django.db import models
from vocab_mode.models import Word  # vocab_mode에서 단어 모델 임포트
from accounts.models import User  # accounts에서 사용자 모델 임포트


# 예문 테이블
class Sentence(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)  # 단어와 연결
    sentence = models.TextField()  # 예문
    meaning = models.TextField()  # 예문 뜻

    def __str__(self):
        return f"{self.word} - {self.sentence}"


# 학습 결과 테이블
class LearningResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와 연결
    category_id = models.IntegerField()  # 테마 ID (카테고리)
    score_by_accuracy = models.FloatField()  # 정오답에 따른 점수
    score_by_word_usage = models.FloatField()  # 단어 사용 빈도에 따른 점수
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 일시

    def __str__(self):
        return f"User: {self.user.username}, Category: {self.category_id}, Score: {self.score_by_accuracy}"

    def calculate_score(self, correct_answers, total_answers, word_usage_frequency):
        # 예시로 계산하는 점수 함수
        self.score_by_accuracy = (correct_answers / total_answers) * 100
        self.score_by_word_usage = (
            word_usage_frequency * 10
        )  # 예시로 단어 사용 빈도에 따른 점수
        self.save()
