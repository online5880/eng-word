"""from django import forms
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

    nickname = forms.CharField(
        label="닉네임", help_text="스펠스타즈에서 사용할 닉네임을 입력하세요."
    )

    username = forms.CharField(
        label="아이디",
    )

    birth_date = forms.DateField(
        label="생년월일",
        widget=forms.DateInput(attrs={"type": "date"}),  # HTML5 달력 입력기
        help_text="생년월일을 선택하세요.",
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

    class Meta:
        model = StudentInfo
        fields = ["nickname", "username", "birth_date", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=True)

        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = StudentInfo
        fields = ["username", "nickname", "birth_date", "password"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),  # Date picker widget
        }
"""
