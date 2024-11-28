import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


# 사용자 모델
class CustomUser(AbstractUser):
    """
    사용자 모델: Django 기본 사용자 모델 확장.
    """
    ROLE_CHOICES = [
        ('student', '학생'),
        ('parent', '학부모'),
    ]

    name = models.CharField(max_length=50, verbose_name='이름', blank=False, default='이름 없음')
    birth_date = models.DateField(verbose_name='생년월일', blank=True, null=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',  # 기본값을 '학생'으로 설정
        verbose_name='역할'
    )

    def __str__(self):
        return f"{self.name or self.username} ({self.role})"

    @property
    def age(self):
        """현재 나이를 계산."""
        if self.birth_date:
            today = date.today()
            return (
                today.year
                - self.birth_date.year
                - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            )
        return None


# 학생 모델
class Student(models.Model):
    """
    학생 프로필 모델: 사용자(CustomUser)에 연결된 1:1 관계.
    """
    GRADE_CHOICES = [
        (1, '1학년'),
        (2, '2학년'),
        (3, '3학년'),
        (4, '4학년'),
        (5, '5학년'),
        (6, '6학년'),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='사용자'
    )
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='학년'
    )
    unique_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='학생 코드'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    def __str__(self):
        return f"{self.user.name} ({self.grade}학년)"

    def get_grade_display(self):
        """학년을 문자열로 반환"""
        for value, display in self.GRADE_CHOICES:
            if value == self.grade:
                return display
        return '미정'


# 학부모 모델
class Parent(models.Model):
    """
    학부모 프로필 모델: 사용자(CustomUser)에 연결된 1:1 관계.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        verbose_name='사용자'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    children = models.ManyToManyField(
        Student,
        through='ParentStudentRelation',
        related_name='parents',
        verbose_name='자녀'
    )

    def __str__(self):
        return f"{self.user.name} ({self.user.username})"


# 학부모-학생 관계 모델
class ParentStudentRelation(models.Model):
    """
    학부모와 학생 간의 관계를 관리하는 모델.
    """
    RELATION_CHOICES = [
        ('아버지', '아버지'),
        ('어머니', '어머니'),
        ('할아버지', '할아버지'),
        ('할머니', '할머니'),
        ('삼촌', '삼촌'),
        ('이모', '이모'),
        ('고모', '고모'),
    ]

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        verbose_name='학부모'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='학생'
    )
    parent_relation = models.CharField(
        max_length=50,
        choices=RELATION_CHOICES,
        default="아버지",
        verbose_name='학부모 관점 관계'
    )
    student_relation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='학생 관점 관계'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        unique_together = ('parent', 'student')

    def save(self, *args, **kwargs):
        # 학부모 관점의 관계에 따라 학생 관점의 관계 자동 설정
        relation_mapping = {
            '아버지': '자녀',
            '어머니': '자녀',
            '할아버지': '손자/손녀',
            '할머니': '손자/손녀',
            '삼촌': '조카',
            '이모': '조카',
            '고모': '조카',
        }
        self.student_relation = relation_mapping.get(self.parent_relation, '자녀')
        super().save(*args, **kwargs)

    def get_relation_display(self, for_user):
        """사용자 유형에 따라 적절한 관계를 반환"""
        if for_user.role == 'parent':
            return self.student_relation
        return self.parent_relation

    def __str__(self):
        return f"{self.parent.user.name}의 {self.student_relation} {self.student.user.name}"

# 학생 로그인/로그아웃 로그 모델
class StudentLog(models.Model):
    """
    학생의 로그인/로그아웃 데이터를 관리하는 모델.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='학생'
    )
    login_time = models.DateTimeField(verbose_name='로그인 시간')
    logout_time = models.DateTimeField(verbose_name='로그아웃 시간', null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.name} - {self.login_time} ~ {self.logout_time or '미로그아웃'}"
    

# 학습 로그 모델
class StudentLearningLog(models.Model):
    """
    학생 학습 로그 모델.
    """
    LEARNING_MODES = [
        (1, "사전 학습"),
        (2, "시험"),
        (3, "발음 연습"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='learning_logs',
        verbose_name='학생'
    )
    learning_mode = models.IntegerField(choices=LEARNING_MODES, verbose_name='학습 모드')
    start_time = models.DateTimeField(verbose_name='시작 시간')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='종료 시간')

    def __str__(self):
        mode = dict(self.LEARNING_MODES).get(self.learning_mode, "알 수 없음")
        return f"{self.student.user.name} - {mode} ({self.start_time} ~ {self.end_time or '진행 중'})"