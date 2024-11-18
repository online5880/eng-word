from django.urls import path

# from .views import signup, profileView
from .views import UserLoginView, signup, UserLogoutView, profileView, StudentLearningLogViewSet, end_learning_session
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"students/(?P<student_pk>\d+)/learning-logs",StudentLearningLogViewSet,basename='learning-log')

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("signup/",signup,name="signup"),
    path("profile/",profileView,name="profile"),
    path("end-learning/", end_learning_session, name="end_learning"),
]
