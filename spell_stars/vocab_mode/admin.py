from django.contrib import admin
from .models import Word, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'category', 'part_of_speech', 'get_meanings']
    list_filter = ['category', 'part_of_speech']  # 카테고리와 품사로 필터링
    search_fields = ['word', 'meanings', 'examples']  # 단어, 의미, 예문으로 검색
    ordering = ['category', 'word']  # 카테고리별, 단어 알파벳순 정렬
    
    def get_meanings(self, obj):
        # JSONField의 meanings를 문자열로 변환하여 표시
        if isinstance(obj.meanings, list):
            return ', '.join(obj.meanings)
        return str(obj.meanings)
    get_meanings.short_description = '의미'  # 컬럼 헤더 이름 설정