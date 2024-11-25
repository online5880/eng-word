import wave
import json
from django.apps import apps
from difflib import SequenceMatcher
import librosa

# 모델
# model = Model("D:/programming/python/chunjae/english_quiz/spell_stars/utils/PronunciationChecker/PC_Pipeline/model/vosk-model-en-us-0.22")
# model = Model("/Users/mane/Documents/프로젝트/eng-word/spell_stars/utils/model/vosk-model-en-us-0.22")
model = apps.get_app_config("spell_stars").whisper_model
processor = apps.get_app_config('spell_stars').whisper_processor

def fine_tuned_whisper(path, model=model, processor=processor):
   
    # 모델 사용 예제
    audio_file = path

    # 오디오 파일 처리
    audio, rate = librosa.load(audio_file, sr=16000)  # Whisper는 16kHz 필요
    inputs = processor(audio, sampling_rate=rate, return_tensors="pt")

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
