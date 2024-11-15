import os
from django.apps import AppConfig
import whisper
import warnings

class SpellStarsConfig(AppConfig):
    name = 'spell_stars'

    def ready(self):
        # 메인 프로세스에서만 실행되도록 설정
        if os.environ.get('RUN_MAIN') == 'true':
            warnings.filterwarnings("ignore", category=FutureWarning)
            print("load whisper")  # 확인용 메시지
            # Whisper 모델을 한 번 로드하고 저장
            self.whisper_model = whisper.load_model("small")
