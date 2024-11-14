from  rest_framework import serializers
from .models import Word, Category

class WordSerializer(serializers.ModelSerializer):
    audio_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Word
        fields = ['word','meanings','part_of_speech','examples','audio_file','audio_file_url']
        
    def get_audio_file_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file:
            return request.build_absolute_uri(f"/media/{obj.audio_file}")
        return None
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    words = WordSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id','name','words']