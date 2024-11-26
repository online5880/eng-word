from rest_framework import serializers
from .models import LearningResult

class LearningResultSerializer(serializers.ModelSerializer):
    word_name = serializers.CharField(source='word.word', read_only=True)  # 단어 이름 추가

    class Meta:
        model = LearningResult
        fields = ['id', 'word_name', 'learning_category', 'learning_date', 'pronunciation_score', 'accuracy_score', 'frequency_score']
