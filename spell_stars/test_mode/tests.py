from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Student
from .models import TestResult, TestResultDetail
from vocab_mode.models import Word
from sent_mode.models import Sentence

class TestModeTests(TestCase):
    def setUp(self):
        # 테스트용 사용자 및 학생 생성
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User'
        )
        self.student = Student.objects.create(
            user=self.user,
            name='Test Student'
        )
        
        # 테스트용 단어와 문장 생성
        self.word = Word.objects.create(
            word='test',
            meanings='시험',
            category=1
        )
        self.sentence = Sentence.objects.create(
            word=self.word,
            sentence='This is a test sentence.',
            sentence_meaning='이것은 테스트 문장입니다.'
        )

    def test_test_mode_view(self):
        # 로그인
        self.client.login(username='testuser', password='testpass123')
        
        # 테스트 모드 페이지 접근
        response = self.client.get(reverse('test_mode'))
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test_mode/test_page.html')
        
    def test_submit_audio(self):
        self.client.login(username='testuser', password='testpass123')
        
        # 오디오 제출 테스트
        with open('path/to/test/audio.wav', 'rb') as audio_file:
            response = self.client.post(reverse('submit_audio'), {
                'audio': audio_file,
                'word': 'test'
            })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('is_correct', response.json())

    def test_calculate_score(self):
        # 점수 계산 로직 테스트
        from .views import calculate_score
        
        score = calculate_score(3, 5, 5)  # 3문제 맞춤, 총 5문제, 최대 점수 5점
        self.assertEqual(score, 3.0)

class TestResultAPITests(TestCase):
    def setUp(self):
        # API 테스트를 위한 설정
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User'
        )
        self.student = Student.objects.create(
            user=self.user,
            name='Test Student'
        )
        
        # 테스트 결과 생성
        self.test_result = TestResult.objects.create(
            student=self.student,
            test_number=1,
            accuracy_score=80
        )

    def test_test_result_list_api(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('test-results'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())

    def test_test_result_detail_api(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('test-result-details', kwargs={'test_id': self.test_result.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['accuracy_score'], 80)
