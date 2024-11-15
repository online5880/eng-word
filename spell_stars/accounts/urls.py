from django.urls import path

# from .views import signup, profileView
from .views import UserLoginView, signup, UserLogoutView, profileView, UserListAPIView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("signup/",signup,name="signup"),
    path("profile/",profileView,name="profile"),
]
