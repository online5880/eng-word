from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class GrammarCorrector:
    def __init__(self):
        # Grammarformer 모델과 토크나이저 초기화
        self.tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")

    def correct_sentence(self, sentence: str) -> str:
        # Grammarformer를 사용하여 문장 교정
        inputs = self.tokenizer(sentence, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=50)
        corrected_sentence = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_sentence
