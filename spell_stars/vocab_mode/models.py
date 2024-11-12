from django.db import models
from django.conf import settings

class Word(models.Model):
    text = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.text if self.text else "Unknown Word"

class VocabularyBook(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    words = models.ManyToManyField(Word)
    json_file = models.FileField(upload_to=r'D:\\workspace\\eng_word\\utils\\json_words\\combined\\combined_word.json', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s Vocabulary Book"

class PronunciationRecord(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField()
    audio_file = models.FileField(upload_to='pronunciation_records/')

    def __str__(self):
        return f"{self.student.username} - {self.word.text} - {self.score}"
