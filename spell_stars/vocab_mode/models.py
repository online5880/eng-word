from django.db import models

# 카테고리 모델
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 카테고리 이름
    def __str__(self):
        return self.name

# 단어 모델
class Word(models.Model):
    category = models.ForeignKey(Category, related_name="words", on_delete=models.CASCADE)  # 카테고리와의 외래키 관계
    word = models.CharField(max_length=100)  # 단어 이름
    meanings = models.JSONField()  # 단어 뜻 (리스트 형태로 저장)
    part_of_speech = models.CharField(max_length=20, blank=True, null=True)  # 품사 (예: 명사, 형용사 등)
    examples = models.JSONField()  # 예문 (영문과 한글 번역 리스트 형태로 저장)
    audio_file = models.CharField(max_length=255, blank=True, null=True)  # 원어민 음성 파일 경로 (파일 경로 유지)
    
    def save(self, *args, **kwargs):
        # audio_file 필드에 파일 경로 자동 추가
        if not self.audio_file:
            self.audio_file = f"audio_files/native/{self.word}.wav"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.word
