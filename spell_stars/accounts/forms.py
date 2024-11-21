import re
from django import forms
from .models import StudentInfo
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label="아이디",
        help_text="아이디는 영어로 시작하며 영어 소문자, 대문자, 숫자만 사용 가능합니다.",
    )
    
    name = forms.CharField(
        label="이름", 
        max_length=30, 
        help_text="이름을 입력하세요.", 
        required=True  # 필수로 설정
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
        widget=forms.DateInput(attrs={"type": "date"}),  # HTML5 달력 입력기
        help_text="생년월일을 선택하세요.",
        required=True,  # 필수로 설정
    )
    
    grade = forms.ChoiceField(
        label="학년",
        choices=[(i, f"{i}학년") for i in range(1, 7)],
        help_text="학년을 선택하세요",
        required=False,
    )

    class Meta:
        model = StudentInfo
        fields = ["username", "name", "birth_date", "grade", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # 영어로 시작하고, 영어와 숫자만 포함 (정규식: ^[a-zA-Z][a-zA-Z0-9]+$)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', username):
            raise forms.ValidationError("아이디는 영어로 시작하며 영어와 숫자만 입력 가능합니다.")
        
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.grade = self.cleaned_data.get("grade")
        
        if commit:
            user.save()
        return user
