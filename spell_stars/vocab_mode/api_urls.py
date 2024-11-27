from django.urls import path
from . import views

urlpatterns = [
    path('words', views.WordListAPIView.as_view(), name='word-list'),  # 단어 목록
    path('categories', views.CategoryListAPIView.as_view(), name='category-list'),  # 카테고리 목록
    path('categories/<str:category_id>', views.WordsByCategoryAPIView.as_view(), name='category-words'),  # 특정 카테고리 단어
]    