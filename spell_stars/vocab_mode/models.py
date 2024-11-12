from django.db import models
from django.conf import settings

class Word(models.Model):
    text = models.CharField(max_length=50, blank=True, null=True)  # 단어 텍스트
    meaning = models.CharField(max_length=255, blank=True, null=True)  # 단어 뜻
    example_sentence = models.TextField(blank=True, null=True)  # 예문
    example_translation = models.TextField(blank=True, null=True)  # 예문 뜻
    audio_file = models.FileField(upload_to='audio_files/native/', blank=True, null=True)  # 원어민 음성 파일 경로
    part_of_speech = models.CharField(max_length=20, blank=True, null=True)  # 품사 정보

    def __str__(self):
        return self.text or "Unknown Word"