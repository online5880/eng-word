from django.db import models


# 카테고리
class Category(models.Model):
    # 카테고리 이름
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# 단어
class Word(models.Model):
    category = models.ForeignKey(Category, related_name="words", on_delete=models.CASCADE) # 카테고리
    word = models.CharField(max_length=100)  # 단어
    meanings = models.JSONField()  # 단어 뜻 - 문자열 또는 리스트 저장 가능
    part_of_speech = models.CharField(max_length=20, blank=True, null=True)  # 품사
    examples = models.JSONField()  # 예문 - 문자열 또는 리스트 저장 가능
    example_translations = models.JSONField()  # 예문 뜻 - 문자열 또는 리스트 저장 가능
    audio_file = models.CharField(max_length=255, blank=True, null=True)  # 원어민 음성 파일 경로

    def __str__(self):
        return self.word