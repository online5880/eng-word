from  rest_framework import serializers
from .models import Word

class WordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Word
        fields = ['word','category','meanings','part_of_speech','examples','file_path']
        
        
class AudioUploadSerializer(serializers.Serializer):
    audio = serializers.FileField(required=True)  # 파일 업로드 필드
    word = serializers.CharField(max_length=100, required=True)  # 단어 필드