import os
import wave
import json
from django.apps import apps
from difflib import SequenceMatcher
<<<<<<< HEAD:spell_stars/utils/PronunciationChecker/Pipeline/vosk_.py
from pathlib import Path

# 모델
current_dir = Path(__file__).parent
model_path = current_dir.parent.parent / "model" / "vosk-model-en-us-0.22"
model = Model(str(model_path))
=======
import librosa

# 모델
# model = Model("D:/programming/python/chunjae/english_quiz/spell_stars/utils/PronunciationChecker/PC_Pipeline/model/vosk-model-en-us-0.22")
# model = Model("/Users/mane/Documents/프로젝트/eng-word/spell_stars/utils/model/vosk-model-en-us-0.22")
model = apps.get_app_config("spell_stars").whisper_model
processor = apps.get_app_config('spell_stars').whisper_processor
>>>>>>> c83b7d859b5eac5d599eea128577fc567b050b69:spell_stars/utils/PronunciationChecker/PC_Pipeline/vosk_.py

def fine_tuned_whisper(path, model=model, processor=processor):
   
    # 모델 사용 예제
    audio_file = path

<<<<<<< HEAD:spell_stars/utils/PronunciationChecker/Pipeline/vosk_.py
def transcribe_audio_vosk(audio_path):
    wf = wave.open(audio_path, "rb")
    if not model:
        print("vosk model이 없습니다.")
        return
    
    recognizer = KaldiRecognizer(model, wf.getframerate())
=======
    # 오디오 파일 처리
    audio, rate = librosa.load(audio_file, sr=16000)  # Whisper는 16kHz 필요
    inputs = processor(audio, sampling_rate=rate, return_tensors="pt")
>>>>>>> c83b7d859b5eac5d599eea128577fc567b050b69:spell_stars/utils/PronunciationChecker/PC_Pipeline/vosk_.py

    # 언어 설정: 특정 언어로 지정하려면 아래처럼 설정
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")

    # 모델 추론
    generated_ids = model.generate(
        inputs["input_features"], 
        forced_decoder_ids=forced_decoder_ids  # 언어 및 작업 설정 반영
    )

    # 결과 변환
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print("Transcription:", transcription)

    return transcription

def evaluate_pronunciation(audio_path, expected_word):
    recognized_text = fine_tuned_whisper(audio_path)
    print(f"Recognized Text: {recognized_text}")

    similarity = SequenceMatcher(None, expected_word.lower(), recognized_text.lower()).ratio()
    phoneme_score = similarity * 100
    print(f"Expected Word: {expected_word}")
    print(f"Phoneme-Level Accuracy Score: {phoneme_score:.2f}%")
    return phoneme_score
