from django.contrib import admin
from .models import Word
# Register your models here.

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'meaning', 'part_of_speech')  # 목록에 표시할 필드
    search_fields = ('text', 'meaning')  # 검색 필드 추가
    list_filter = ('part_of_speech',)  # 필터 추가