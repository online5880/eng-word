from django.db import models
from vocab_mode.models import Word


class PronunciationPractice(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
