from django.contrib import admin
from .models import Sentence, LearningResult

# Sentence 모델의 관리 인터페이스 커스터마이즈
class SentenceAdmin(admin.ModelAdmin):
    # 리스트에서 표시할 필드들
    list_display = ('word', 'sentence', 'sentence_meaning')
    
    # 필드를 클릭할 수 있는 링크로 설정
    list_display_links = ('sentence',)
    
    # 필터 추가
    list_filter = ('word',)
    
    # 검색 필드 설정 (예문에서 검색할 수 있도록)
    search_fields = ('sentence', 'sentence_meaning')

# LearningResult 모델의 관리 인터페이스 커스터마이즈
class LearningResultAdmin(admin.ModelAdmin):
    # 리스트에서 표시할 필드들
    list_display = ('word', 'student', 'learning_category', 'learning_date', 'pronunciation_score', 'accuracy_score', 'frequency_score')
    
    # 필드를 클릭할 수 있는 링크로 설정
    list_display_links = ('student',)
    
    # 필터 추가
    list_filter = ('word', 'student', 'learning_category', 'learning_date')
    
    # 검색 필드 설정 (학생 및 단어에서 검색할 수 있도록)
    search_fields = ('student__name', 'word__word', 'learning_category')

# 모델을 admin에 등록
admin.site.register(Sentence, SentenceAdmin)
admin.site.register(LearningResult, LearningResultAdmin)
