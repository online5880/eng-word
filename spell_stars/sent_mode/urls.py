from django.urls import path
from . import views

urlpatterns = [
    path("", views.example_sentence_learning, name="example_sentence_learning"),
    path('upload_audio/', views.upload_audio, name='upload_audio'),
]
