from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'nickname', 'birth_date', 'date_joined']
        
class UserCreationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(required=True)  # 생년월일 필드

    class Meta:
        model = User
        fields = ['username', 'nickname', 'birth_date', 'password1', 'password2']
        
    # 유효성 검사    
    def validate(self, data):
        # password1과 password2가 일치하는지 확인
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # 생년월일을 통해 나이 유효성 검사
        if 'birth_date' in data:
            today = date.today()
            birth_date = data['birth_date']
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 5 or age > 100:
                raise serializers.ValidationError("나이는 5 ~ 100 사이여야 합니다.")

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
            nickname=validated_data.get('nickname', ''),
            birth_date=validated_data.get('birth_date')  # birth_date로 저장
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user
