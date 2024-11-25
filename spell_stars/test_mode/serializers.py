from rest_framework import serializers
from .models import TestResult, TestResultDetail
from accounts.models import Student
from vocab_mode.models import Word
from sent_mode.models import Sentence

class TestResultDetailSerializer(serializers.ModelSerializer):
    word = serializers.StringRelatedField()  # Word 모델의 텍스트를 직렬화
    sentence = serializers.StringRelatedField()  # Sentence 모델의 텍스트를 직렬화

    class Meta:
        model = TestResultDetail
        fields = ['id', 'word', 'sentence', 'sentence_meaning', 'is_correct']

class TestResultSerializer(serializers.ModelSerializer):
    details = TestResultDetailSerializer(many=True, read_only=True)  # TestResult에 연결된 TestResultDetail들

    class Meta:
        model = TestResult
        fields = ['id', 'student', 'test_number', 'test_date', 'accuracy_score', 'details']
