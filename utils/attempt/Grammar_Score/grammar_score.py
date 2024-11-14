import spacy
from transformers import BertForSequenceClassification, BertTokenizer
from typing import Dict, Tuple
import re
from collections import Counter


class AdvancedGrammarScorer:
    def __init__(self):
        # 기본 NLP 파이프라인 로드
        self.nlp = spacy.load("en_core_web_lg")
        
        # Transformer 기반 문법 오류 탐지 모델 설정 (예시: BERT CoLA 모델)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.grammar_model = BertForSequenceClassification.from_pretrained("textattack/bert-base-uncased-CoLA")
        
        # 평가 항목 가중치 설정
        self.weights = {
            "basic_requirements": 0.15,
            "sentence_structure": 0.2,
            "word_count": 0.1,
            "complexity": 0.1,
            "lexical_diversity": 0.05,
            "semantic_coherence": 0.25,
            "meaningful_words": 0.15
        }

    def score_sentence(self, sentence: str) -> Tuple[float, Dict]:
        doc = self.nlp(sentence)
        scores = {}
        
        # 1. 기본 검사
        basic_checks = {
            "starts_with_capital": sentence[0].isupper(),
            "ends_with_punctuation": sentence.rstrip()[-1] in ".!?",
            "no_multiple_punctuation": not any(c*2 in sentence for c in ".!?")
        }
        scores["basic_requirements"] = sum(basic_checks.values()) / len(basic_checks)
        
        # 2. 문장 구조 검사
        structure_checks = {
            "has_subject": any(token.dep_ in ["nsubj", "nsubjpass"] for token in doc),
            "has_verb": any(token.pos_ == "VERB" for token in doc),
            "verb_agreement": self._check_verb_agreement(doc)
        }
        scores["sentence_structure"] = sum(structure_checks.values()) / len(structure_checks)
        
        # 3. 단어 수 검사 (5~8개 목표)
        word_count = len([token for token in doc if not token.is_punct])
        scores["word_count"] = self._score_word_count(word_count)
        
        # 4. 문장 복잡도 검사
        complexity_scores = {
            "vocabulary_level": self._check_vocabulary_level(doc),
            "sentence_complexity": self._check_sentence_complexity(doc)
        }
        scores["complexity"] = sum(complexity_scores.values()) / len(complexity_scores)
        
        # 5. 어휘 다양성 검사
        scores["lexical_diversity"] = self._calculate_lexical_diversity(doc)
        
        # 6. 의미론적 코히런스 검사 (Transformer 기반 문법 오류 탐지)
        scores["semantic_coherence"] = self._semantic_coherence_score(sentence)
        
        # 7. 의미 있는 단어 검사 (강화된 의미 없는 단어 감지 및 반복 단어 검사)
        scores["meaningful_words"] = self._enhanced_meaningful_words_score(doc)
        
        # 최종 점수 계산
        final_score = sum(score * self.weights[category] for category, score in scores.items())
        
        return round(final_score, 2), scores

    def _check_verb_agreement(self, doc) -> bool:
        for token in doc:
            if token.dep_ == "nsubj":
                head = token.head
                if head.pos_ == "VERB":
                    return True
        return False

    def _score_word_count(self, count: int) -> float:
        if 5 <= count <= 8:
            return 1.0
        elif count < 5:
            return max(0, count / 5)
        else:
            return max(0, 1 - (count - 8) / 4)

    def _check_vocabulary_level(self, doc) -> float:
        simple_words = sum(1 for token in doc if len(token.text) <= 6)
        total_words = sum(1 for token in doc if not token.is_punct)
        return simple_words / total_words if total_words > 0 else 0

    def _check_sentence_complexity(self, doc) -> float:
        clause_count = sum(1 for token in doc if token.dep_ == "ROOT")
        return 1.0 if clause_count == 1 else 0.5 if clause_count == 2 else 0.0

    def _calculate_lexical_diversity(self, doc) -> float:
        words = [token.text.lower() for token in doc if token.is_alpha]
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0

    def _semantic_coherence_score(self, sentence: str) -> float:
        inputs = self.tokenizer(sentence, return_tensors="pt")
        outputs = self.grammar_model(**inputs)
        prediction = outputs.logits.argmax().item()
        return 1.0 if prediction == 1 else 0.0

    def _enhanced_meaningful_words_score(self, doc) -> float:
        """
        강화된 의미 없는 단어 감지 및 반복 단어 패턴 검사:
        - is_oov로 사전에 없는 단어 확인
        - 특정 길이 이상의 반복적인 문자열 감지
        - 반복 패턴 검사
        """
        meaningless_words = 0
        total_words = 0
        word_counts = Counter([token.text.lower() for token in doc if token.is_alpha])
        
        for token in doc:
            if not token.is_punct:
                total_words += 1
                # 사전에 없는 단어인지 확인
                if token.is_oov:
                    meaningless_words += 1
                # 반복되는 문자 패턴 감지 (예: asdfasdf, aaaaaa)
                elif len(token.text) > 10 or re.match(r"(.+?)\1{2,}", token.text):
                    meaningless_words += 1
                # 단어의 모든 문자가 동일한 경우 (예: "aaaaaa")
                elif re.match(r"^(.)\1+$", token.text):
                    meaningless_words += 1
                # 같은 단어가 3번 이상 반복될 경우 감점
                elif word_counts[token.text.lower()] > 2:
                    meaningless_words += 1
        
        return max(0, 1 - (meaningless_words / total_words)) if total_words > 0 else 0
