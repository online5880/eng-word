import json
import os
from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    meanings = models.JSONField(default=dict)  # 여러 개의 뜻을 저장
    part_of_speech = models.CharField(max_length=50, blank=True, null=True) # 품사
    category = models.IntegerField(blank=True, null=True)  # 카테고리
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
                    file_path=os.path.join('audio_files/native', f"{word}.wav")
                )
                
    @classmethod
    def update_file_paths(cls):
        # 모든 인스턴스를 가져와서 file_path를 일괄 변경
        for instance in cls.objects.all():
            # 기존 파일 이름을 가져와 새로운 경로로 설정
            filename = os.path.basename(instance.file_path)
            new_path = os.path.join('audio_files/native', filename)
            instance.file_path = new_path
            instance.save()