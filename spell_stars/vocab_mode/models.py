import json
import os
from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    meanings = models.JSONField(default=dict)  # 여러 개의 뜻을 저장
    part_of_speech = models.CharField(max_length=50, blank=True, null=True) # 품사
    category = models.IntegerField() # 카테고리
    examples = models.JSONField(default=dict)  # 영어와 한국어 예문을 저장
    file_path = models.CharField(max_length=255, blank=True, null=True)  # 파일 경로를 저장

    def __str__(self):
        return self.word
    
    @property
    def audio_file_path(self):
        return os.path.join('media/audio_files/native', f"{self.word}.wav")

    @classmethod
    def load_words_from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for word, details in data.items():
                cls.objects.create(
                    word=word,
                    meanings=details.get('meanings', []),
                    part_of_speech=details.get('part_of_speech', ''),
                    category=details.get('category', 0),
                    examples=details.get('examples', []),
                    file_path=os.path.join('media/audio_files/native', f"{word}.wav")
                )