import os
import sys
from django.conf import settings

# utils 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(settings.BASE_DIR, '..')))

# PronunciationChecker 모킹
class MockPronunciationChecker:
    def process_audio_files(self, *args, **kwargs):
        return {
            'formant_score': 80,
            'phoneme_score': 90,
            'overall_score': 85
        }

# 테스트에서 사용할 설정 오버라이드
def pytest_configure():
    settings.PRONUNCIATION_CHECKER = MockPronunciationChecker() 