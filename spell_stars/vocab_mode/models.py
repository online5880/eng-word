from django.db import models
from django.conf import settings

class Word(models.Model):
    text = models.CharField(max_length=50, blank=True, null=True)  # 단어 텍스트
    meaning = models.CharField(max_length=255, blank=True, null=True)  # 단어 뜻
    example_sentence = models.TextField(blank=True, null=True)  # 예문
    example_translation = models.TextField(blank=True, null=True)  # 예문 뜻

    def __str__(self):
        return self.text or "Unknown Word"


class VocabularyBook(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 학생(사용자)와 연결
    words = models.ManyToManyField(Word)  # 여러 단어와 연결
    created_at = models.DateTimeField(auto_now_add=True)  # 단어장 생성 시간

    def __str__(self):
        return f"{self.student.username}'s Vocabulary Book"

class PronunciationRecord(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField()
    audio_file = models.FileField(upload_to='pronunciation_records/')

    def __str__(self):
        return f"{self.student.username} - {self.word.text} - {self.score}"
