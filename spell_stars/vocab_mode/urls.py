# urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('vocab_mode/', views.display_vocabulary_book, name='vocab_mode'),
    path('vocab_mode/upload_audio/', views.upload_audio, name='vocab_upload_audio'),
    path('vocab_mode/random_category/', views.display_vocabulary_book_random_category, name='vocab_random_category'),
    # path('api/words/',views.WordListAPIView.as_view(),name='word-list'),
    # path('api/categories/',views.CategoryListAPIView.as_view(),name='category-list'),
    # path('api/categories/<int:id>',views.CategoryListAPIView.as_view(),name='category-list')
]
