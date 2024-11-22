from  rest_framework import serializers
from .models import Word

class WordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Word
        fields = ['word','category','meanings','part_of_speech','examples','file_path']