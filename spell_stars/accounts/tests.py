from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from accounts.models import Student, StudentLearningLog
from django.utils import timezone

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User',
        )
        self.student = Student.objects.create(
            user=self.user,
            unique_code="abc"
        )

    @patch('vocab_mode.views.process_audio_files')
    def test_login_view(self, mock_process_audio):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_student_learning_log(self):
        self.client.force_login(self.user)
        log = StudentLearningLog.objects.create(
            student=self.student,
            learning_mode=1,
            start_time=timezone.now()
        )
        
        self.assertEqual(log.learning_mode, 1)
        self.assertIsNone(log.end_time)

    def test_student_profile(self):
        self.client.force_login(self.user)
        self.assertEqual(self.student.user.name, 'Test User')
        self.assertEqual(self.student.user, self.user)
