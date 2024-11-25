import re
from django import forms
from .models import CustomUser, Student, ParentStudentRelation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', '학생'),
        ('parent', '학부모'),
    ]
    GRADE_CHOICES = [
        (1, '1학년'),
        (2, '2학년'),
        (3, '3학년'),
        (4, '4학년'),
        (5, '5학년'),
        (6, '6학년'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        required=True,
        initial='student'
    )
    student_code = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '학부모만 입력'}),
    )
    username = forms.CharField(
        label="아이디",
        help_text="아이디는 영어로 시작하며 영어 소문자, 대문자, 숫자만 사용 가능합니다.",
    )
    name = forms.CharField(
        label="이름",
        max_length=30,
        help_text="이름을 입력하세요.",
        required=True,
    )
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput,
        help_text="8자 이상의 비밀번호를 입력하세요. 다른 개인 정보와 유사하지 않은 비밀번호를 사용하세요.",
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput,
        help_text="확인을 위해 이전과 동일한 비밀번호를 입력하세요.",
    )
    birth_date = forms.DateField(
        label="생년월일",
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="생년월일을 선택하세요.",
        required=True,
    )
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        label='학년',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ["username", "name", "birth_date", "password1", "password2", "role", "student_code", "grade"]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        grade = cleaned_data.get('grade')
        student_code = cleaned_data.get('student_code', "").strip()
        username = cleaned_data.get('username', "")

        # 아이디 유효성 검사
        if not username:
            raise forms.ValidationError("아이디를 입력하세요.")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', username):
            raise forms.ValidationError("아이디는 영어로 시작하며 영어와 숫자만 입력 가능합니다.")

        # 학부모 역할일 경우
        if role == 'parent':
            if not student_code:
                raise forms.ValidationError("학부모 역할을 선택하면 학생 코드를 입력해야 합니다.")
            from .models import Student
            if not Student.objects.filter(unique_code=student_code).exists():
                raise forms.ValidationError("유효하지 않은 학생 코드입니다.")

        if role == 'student' and not grade:
            raise forms.ValidationError("학생의 경우 학년을 선택해야 합니다.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        student_code = self.cleaned_data.get('student_code', "").strip()
        grade = self.cleaned_data.get('grade')

        # 사용자 역할 설정
        if role:
            user.role = role

        if commit:
            user.save()
            # 역할에 따른 추가 작업
            if role == 'student':
                from .models import Student
                Student.objects.create(user=user)
            elif role == 'parent' and student_code:
                from .models import Parent, Student, ParentStudentRelation
                parent = Parent.objects.create(user=user)
                student = Student.objects.get(unique_code=student_code)
                ParentStudentRelation.objects.create(parent=parent, student=student)

        return user


class AddChildForm(forms.Form):
    student_code = forms.CharField(
        label="자녀 코드",
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '자녀의 고유 코드를 입력하세요'
        })
    )
    parent_relation = forms.ChoiceField(
        label="관계",
        choices=ParentStudentRelation.RELATION_CHOICES,
        initial="부모",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_student_code(self):
        student_code = self.cleaned_data.get('student_code')
        try:
            student = Student.objects.get(unique_code=student_code)
            return student_code
        except Student.DoesNotExist:
            raise forms.ValidationError("유효하지 않은 학생 코드입니다.")

