from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


# 의미 일관성 및 문법 평가 함수
def measure_sc(sentence):
    # 프롬프트
    prompt = (
        f"Evaluate the following sentence for and semantic coherence. "
        f"Answer only '1' if the sentence is semantically coherent. "
        f"Answer only '0' if the sentence lacks coherence.\n\n"
        f"Sentence: '{sentence}'\n\nAnswer with '1' or '0' only:"
    )

    # 모델 입력
    inputs = tokenizer(prompt, return_tensors="pt")

    # 모델 예측 생성
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=5)

    # 점수
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # 0 또는 1로 변환
    if response_text == "1":
        return 1
    elif response_text == "0":
        return 0
    else:
        return None  # 예상치 못한 응답이 있을 경우 None 반환
