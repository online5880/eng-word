from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import Student, CustomUser
from sent_mode.models import LearningResult
from test_mode.models import TestResult
from django.utils import timezone
from datetime import timedelta

# Create your views here.

@login_required
def index(request):
    return render(request,"main/index.html")

@staff_member_required
def export_students(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_{timezone.localtime().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', '이름', '학년', '생년월일', '가입일'])
    
    students = Student.objects.select_related('user').all()
    for student in students:
        writer.writerow([
            student.user.username,
            student.user.name,
            student.user.get_grade_display(),
            student.user.birth_date,
            timezone.localtime(student.created_at).strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    return response

@staff_member_required
def export_learning_results(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="learning_results_{timezone.localtime().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['학생ID', '학생이름', '학습일', '학습유형', '발음점수', '정확도점수'])
    
    results = LearningResult.objects.select_related('student__user').all()
    for result in results:
        writer.writerow([
            result.student.user.username,
            result.student.user.name,
            timezone.localtime(result.learning_date).strftime("%Y-%m-%d %H:%M:%S"),
            result.learning_category,
            result.pronunciation_score,
            result.accuracy_score
        ])
    
    return response

@staff_member_required
def export_test_results(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="test_results_{timezone.localtime().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['학생ID', '학생이름', '시험번호', '시험일', '정확도'])
    
    results = TestResult.objects.select_related('student__user').all()
    for result in results:
        writer.writerow([
            result.student.user.username,
            result.student.user.name,
            result.test_number,
            timezone.localtime(result.test_date).strftime("%Y-%m-%d %H:%M:%S"),
            result.accuracy_score
        ])
    
    return response