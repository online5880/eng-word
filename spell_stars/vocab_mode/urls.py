# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_vocabulary_book, name='vocab_mode'),
    path('upload_audio', views.upload_audio, name='vocab_upload_audio'),
    path('random_category', views.display_vocabulary_book_random_category, name='vocab_random_category'),
]
