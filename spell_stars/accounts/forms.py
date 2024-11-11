from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="사용자 이름",
        widget=forms.TextInput(attrs=({"class":"form-control"}))
    )
    
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"class":"form-control"})
    )
    
class SignupForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ["nickname","username","password1","password2"]
        
    def save(self, commit=True):
        user = super().save(commit=True)
        
        if commit:
            user.save()
        return user