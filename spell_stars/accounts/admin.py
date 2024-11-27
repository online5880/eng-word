from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Parent, ParentStudentRelation, StudentLog

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'name', 'email', 'role', 'birth_date')  # 'grade' 제거
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('name', 'role', 'birth_date')}),  # 'grade' 제거
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('name', 'role', 'birth_date')}),  # 'grade' 제거
    )

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade', 'unique_code', 'created_at')  # 'grade' 추가
    search_fields = ('user__username', 'user__name', 'unique_code')
    list_filter = ('grade', 'created_at')  # 'grade' 필터 추가

class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__name')
    list_filter = ('created_at',)

class ParentStudentRelationAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'parent_relation', 'student_relation', 'created_at')
    search_fields = ('parent__user__name', 'student__user__name')
    list_filter = ('created_at', 'parent_relation')

class StudentLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'login_time', 'logout_time')
    list_filter = ('login_time', 'logout_time')
    search_fields = ('student__user__name',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(ParentStudentRelation, ParentStudentRelationAdmin)
admin.site.register(StudentLog, StudentLogAdmin)
