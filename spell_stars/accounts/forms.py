import re
from uuid import UUID
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Parent, Student, ParentStudentRelation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', '학생'),
        ('parent', '학부모'),
    ]
    GRADE_CHOICES = [
        (1, '1학년'),
        (2, '2학년'),
        (3, '3학년'),
        (4, '4학년'),
        (5, '5학년'),
        (6, '6학년'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        required=True,
        initial='student',
        label="계정 유형"
    )
    student_code = forms.UUIDField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '자녀의 고유 코드를 입력해주세요.'}),
        label="자녀 고유 코드",
        error_messages={
            'invalid': "올바른 UUID 형식이 아닙니다. 예: 123e4567-e89b-12d3-a456-426614174000"
        }
    )
    username = forms.CharField(
        label="아이디",
        help_text="아이디는 영어로 시작하며 영어 소문자, 대문자, 숫자만 사용 가능합니다.",
    )
    name = forms.CharField(
        label="이름",
        max_length=30,
        help_text="이름을 입력하세요.",
        required=True,
    )
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput,
        help_text="8자 이상의 비밀번호를 입력하세요. 다른 개인 정보와 유사하지 않은 비밀번호를 사용하세요.",
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput,
        help_text="확인을 위해 이전과 동일한 비밀번호를 입력하세요.",
    )
    birth_date = forms.DateField(
        label="생년월일",
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="생년월일을 선택하세요.",
        required=True,
    )
    grade = forms.TypedChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        label='학년',
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "name", "birth_date", "password1", "password2", "role", "student_code", "grade"]

    def clean_student_code(self):
        student_code = self.cleaned_data.get('student_code')

        if student_code:
            try:
                UUID(str(student_code), version=4)
            except ValueError:
                raise ValidationError("올바른 UUID 형식이 아닙니다.")
            
            if not Student.objects.filter(unique_code=student_code).exists():
                raise ValidationError("유효하지 않은 학생 코드입니다.")

        return student_code

    def clean_username(self):
        username = self.cleaned_data.get("username")
        User = get_user_model()

        if not username:
            raise ValidationError("아이디를 입력하세요.")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', username):
            raise ValidationError("아이디는 영어로 시작하며 영어와 숫자만 입력 가능합니다.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("이미 사용 중인 아이디입니다.")
        
        return username

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        grade = cleaned_data.get('grade')

        # 학생 역할 검증
        if role == 'student' and not grade:
            raise ValidationError("학생의 경우 학년을 선택해야 합니다.")

        return cleaned_data

    def save(self, commit=True):
        try:
            with transaction.atomic():
                user = super().save(commit=False)
                user.role = self.cleaned_data.get('role')
                
                if commit:
                    user.save()
                    role = self.cleaned_data.get('role')
                    grade = self.cleaned_data.get('grade')
                    student_code = self.cleaned_data.get('student_code')
                    
                    if role == 'student':
                        grade_int = int(grade) if grade else None
                        student = Student.objects.create(
                            user=user,
                            grade=grade_int
                        )
                        print(f"학생 프로필 생성 완료: {student.user.username}, 학년: {student.grade}")
                    elif role == 'parent' and student_code:
                        parent = Parent.objects.create(user=user)
                        try:
                            student = Student.objects.get(unique_code=student_code)
                            ParentStudentRelation.objects.create(
                                parent=parent,
                                student=student
                            )
                        except Student.DoesNotExist:
                            user.delete()
                            raise ValidationError("유효하지 않은 학생 코드입니다.")
                
                return user
                
        except Exception as e:
            print(f"사용자 생성 중 오류 발생: {str(e)}")
            raise


class AddChildForm(forms.Form):
    student_code = forms.CharField(
        label="자녀 코드",
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '자녀의 고유 코드를 입력하세요'
        })
    )
    parent_relation = forms.ChoiceField(
        label="관계",
        choices=ParentStudentRelation.RELATION_CHOICES,
        initial="부모",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_student_code(self):
        student_code = self.cleaned_data.get('student_code')
        try:
            student = Student.objects.get(unique_code=student_code)
            return student_code
        except Student.DoesNotExist:
            raise forms.ValidationError("유효하지 않은 학생 코드입니다.")

