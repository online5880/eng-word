import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Whisper 모델 초기화
MODEL_PATH = "oxorudo/whisper_ssokssokword"  # 사용할 Whisper 모델의 이름
model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
processor = WhisperProcessor.from_pretrained(MODEL_PATH)

def fine_tuned_whisper(path, model=model, processor=processor):
    """
    Whisper STT 모델을 사용하여 오디오 파일을 텍스트로 변환합니다.

    Args:
        path (str): 오디오 파일의 경로
        model: Whisper 모델 객체
        processor: Whisper 프로세서 객체

    Returns:
        str: STT로 변환된 텍스트
    """
    # 오디오 파일 처리
    audio, rate = librosa.load(path, sr=16000)  # Whisper는 16kHz 샘플링 필요
    inputs = processor(audio, sampling_rate=rate, return_tensors="pt")

    # 언어 설정
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")

    # 텍스트 생성
    generated_ids = model.generate(
        inputs["input_features"],
        forced_decoder_ids=forced_decoder_ids
    )
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return transcription
