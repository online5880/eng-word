from rest_framework import serializers
from .models import ParentStudentRelation, Student, StudentLog, StudentLearningLog

# 학생 기본 정보 Serializer
class StudentSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField(source="user.age")  # 사용자 나이 속성 가져오기
    username = serializers.ReadOnlyField(source="user.username")  # 사용자 이름 가져오기
    name = serializers.ReadOnlyField(source="user.name")  # 사용자 이름 가져오기

    class Meta:
        model = Student
        fields = ['id', 'username', 'name', 'unique_code', 'age', 'created_at']

# 학생 로그 Serializer
class StudentLogSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.name')  # 학생 이름

    class Meta:
        model = StudentLog
        fields = ['id', 'student', 'student_name', 'login_time', 'logout_time']


# 학생 학습 로그 Serializer
class StudentLearningLogSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.name')  # 학생 이름
    mode_display = serializers.CharField(source='get_learning_mode_display', read_only=True)  # 학습 모드 이름

    class Meta:
        model = StudentLearningLog
        fields = ['id', 'student', 'student_name', 'learning_mode', 'mode_display', 'start_time', 'end_time']
        
        
class ParentStudentRelationSerializer(serializers.ModelSerializer):
    # 학부모와 학생의 이름을 추가적으로 노출
    parent_name = serializers.ReadOnlyField(source='parent.user.name')
    student_name = serializers.ReadOnlyField(source='student.user.name')

    class Meta:
        model = ParentStudentRelation
        fields = ['id', 'parent', 'parent_name', 'student', 'student_name', 'parent_relation', 'student_relation', 'created_at']

