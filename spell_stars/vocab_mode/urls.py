# urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("vocab_mode/", views.display_vocabulary_book, name="vocab_mode"),  # 단어 학습 페이지
    # path('upload_audio/', views.upload_audio, name='upload_audio'),
    # path('api/words/',views.WordListAPIView.as_view(),name='word-list'),
    # path('api/categories/',views.CategoryListAPIView.as_view(),name='category-list'),
    # path('api/categories/<int:id>',views.CategoryListAPIView.as_view(),name='category-list')
]
