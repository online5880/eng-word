from django.contrib import admin
from .models import TestResult

# TestResult 모델을 admin에 등록
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_number', 'test_date', 'accuracy_score')  # 테이블에서 보여줄 필드
    search_fields = ('student__name',)  # student 이름으로 검색 가능
    list_filter = ('test_date', 'accuracy_score')  # 필터 추가 (test_date, accuracy_score 기준)

admin.site.register(TestResult, TestResultAdmin)
