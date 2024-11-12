# models.py
from django.db import models
from django.conf import settings

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Word(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    pronunciation_guide = models.TextField()
    meaning = models.TextField()  # 뜻 필드 추가
    audio_file = models.FileField(upload_to='word_audios/', null=True, blank=True)  # 네이티브 오디오 필드 추가

    def __str__(self):
        return self.text

class VocabularyBook(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    words = models.ManyToManyField(Word)
    json_file = models.FileField(upload_to='utils/combined_words.json', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s Vocabulary Book"

class PronunciationRecord(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField()
    audio_file = models.FileField(upload_to='pronunciation_records/')

    def __str__(self):
        return f"{self.student.username} - {self.word.text} - {self.score}"
