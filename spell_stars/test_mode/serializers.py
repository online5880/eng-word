from rest_framework import serializers
from .models import TestResult, TestResultDetail

class TestResultDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResultDetail
        fields = ['word', 'sentence', 'sentence_meaning', 'is_correct']

class TestResultSerializer(serializers.ModelSerializer):
    details = TestResultDetailSerializer(many=True, read_only=True)

    class Meta:
        model = TestResult
        fields = ['test_number', 'test_date', 'accuracy_score', 'details']
