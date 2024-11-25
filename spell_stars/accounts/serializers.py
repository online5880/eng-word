from rest_framework import serializers
from .models import Student, StudentLog, StudentLearningLog

# 학생 기본 정보 Serializer
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'username', 'name', 'birth_date', 'grade', 'age', 'derived_grade']

# 학생 로그 Serializer
class StudentLogSerializer(serializers.ModelSerializer):
    # 학생 이름을 표시하기 위해 student 필드를 직렬화
    student_name = serializers.ReadOnlyField(source='student.name')

    class Meta:
        model = StudentLog
        fields = ['id', 'student', 'student_name', 'login_time', 'logout_time']
        extra_kwargs = {
            'student': {'write_only': True},  # POST 시 student_id를 전달
        }

# 학생 학습 로그 Serializer
class StudentLearningLogSerializer(serializers.ModelSerializer):
    # 학생 이름을 표시하기 위해 student 필드를 직렬화
    student_name = serializers.ReadOnlyField(source='student.name')

    class Meta:
        model = StudentLearningLog
        fields = ['id', 'student', 'student_name', 'learning_mode', 'start_time', 'end_time']
        extra_kwargs = {
            'student': {'write_only': True},  # POST 시 student_id를 전달
        }
