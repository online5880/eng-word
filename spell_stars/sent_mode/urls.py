from django.urls import path
from . import views

urlpatterns = [
    path("example_learning/", views.example_learning, name="example_learning"),
]
