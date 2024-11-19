from django.contrib import admin
from .models import Word

# Word 모델의 관리 인터페이스 커스터마이즈
class WordAdmin(admin.ModelAdmin):
    # 리스트에서 표시할 필드들
    list_display = ('word', 'part_of_speech', 'category', 'get_meanings', 'get_examples', 'audio_file_path')
    
    # 필드를 클릭할 수 있는 링크로 설정
    list_display_links = ('word',)
    
    # 필터 추가
    list_filter = ('category', 'part_of_speech')
    
    # 검색 필드 설정 (단어를 검색할 수 있도록)
    search_fields = ('word', 'meanings')
    
    # 필드 정의 (각 필드의 포맷을 정의)
    def get_meanings(self, obj):
        return ", ".join(obj.meanings)
    get_meanings.short_description = "Meanings"  # 열 이름을 설정
    
    def get_examples(self, obj):
        # obj.examples가 리스트인 경우, 각 항목을 쉼표로 구분하여 반환
        return ", ".join(str(example) for example in obj.examples)

    get_examples.short_description = "Examples"

    # 읽기 전용 필드를 관리 인터페이스에 표시
    readonly_fields = ('audio_file_path',)

# 모델을 admin에 등록
admin.site.register(Word, WordAdmin)
