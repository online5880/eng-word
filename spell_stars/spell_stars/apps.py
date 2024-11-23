import os
from django.apps import AppConfig
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import warnings

class SpellStarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spell_stars'
    whisper_model = None
    whisper_processor = None
    def ready(self):
        # 메인 프로세스에서만 실행되도록 설정
        if os.environ.get('RUN_MAIN') == 'true':
            warnings.filterwarnings("ignore", category=FutureWarning)
            print("load whisper")  # 확인용 메시지
            # Whisper 모델을 한 번 로드하고 저장
            self.whisper_model = WhisperForConditionalGeneration.from_pretrained('oxorudo/whisper_ssokssokword')
            self.whisper_processor = WhisperProcessor.from_pretrained('oxorudo/whisper_ssokssokword')
