from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from .forms import LoginForm, SignupForm
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from .models import User
from .serializers import UserSerializer
# Create your views here.

# 로그인뷰
class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    
class UserLogoutView(LogoutView):
    next_page = "/"
    
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("/")
    else:
        form = SignupForm()
    return render(request,"accounts/signup.html",{"form":form})

@login_required
def profileView(request):
    return render(request,"accounts/profile.html",{"user":request.user})

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer