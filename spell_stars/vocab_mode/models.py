from django.db import models


# 단어 테이블
class Word(models.Model):
    word = models.CharField(max_length=100)
    meaning = models.TextField()
    basic_example = models.TextField()
    example_meaning = models.TextField()
    category = models.IntegerField()

    def __str__(self):
        return self.word
