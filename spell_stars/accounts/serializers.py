from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','nickname','date_joined']
        
class UserCreationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username','nickname','password1','password2']
        
    # 유효성 검사    
    def validate(self, data):
        # password1과 password2가 일치하는지 확인
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        # Django의 기본 비밀번호 검증기 적용
        try:
            validate_password(data['password1'])
        except ValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})

        return data
    
    # 생성
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            nickname=validated_data.get('nickname',''),
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user