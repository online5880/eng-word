import os
import wave
import json
from vosk import Model, KaldiRecognizer
from difflib import SequenceMatcher
from pathlib import Path

# 모델
current_dir = Path(__file__).parent
model_path = current_dir.parent.parent / "model" / "vosk-model-en-us-0.22"
model = Model(str(model_path))

def transcribe_audio_vosk(audio_path):
    wf = wave.open(audio_path, "rb")
    if not model:
        print("vosk model이 없습니다.")
        return
    
    recognizer = KaldiRecognizer(model, wf.getframerate())

    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print(f"Intermediate Result: {result.get('text', '')}")  # 중간 결과 출력
            result_text += result.get("text", "") + " "

    final_result = json.loads(recognizer.FinalResult())
    result_text += final_result.get("text", "")
    print(f"Final Transcribed Text: {result_text}")  # 최종 결과 출력
    return result_text

def evaluate_pronunciation(audio_path, expected_word):
    recognized_text = transcribe_audio_vosk(audio_path)
    print(f"Recognized Text: {recognized_text}")

    similarity = SequenceMatcher(None, expected_word.lower(), recognized_text.lower()).ratio()
    phoneme_score = similarity * 100
    print(f"Expected Word: {expected_word}")
    print(f"Phoneme-Level Accuracy Score: {phoneme_score:.2f}%")
    return phoneme_score
