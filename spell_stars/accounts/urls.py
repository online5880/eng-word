from django.urls import path
from .views import UserLoginView,signup,UserLogoutView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("signup/",signup,name="signup")
]
