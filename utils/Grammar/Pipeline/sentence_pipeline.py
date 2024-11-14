import pandas as pd
from Pipeline.grammar_score import AdvancedGrammarScorer  # 문법 검사 클래스
from Pipeline.consistency import measure_sc  # 의미 일관성 검사 함수
from Pipeline.grammar_corrector import GrammarCorrector # Grammarformer를 사용한 문장 보완 클래스


class SentenceEvaluationPipeline:

    def __init__(self,
                 grammar_threshold: float = 0.9,
                 coherence_threshold: int = 1):
        self.grammar_scorer = AdvancedGrammarScorer()  # 문법 점수 측정
        self.coherence_checker = measure_sc  # 의미 일관성 점검 함수
        self.grammar_threshold = grammar_threshold  # 문법 점수 기준
        self.coherence_threshold = coherence_threshold  # 일관성 기준
        self.grammar_corrector = GrammarCorrector()  # GrammarCorrector 초기화

    def evaluate_and_correct(self, sentence: str):
        # 문법 점수 계산
        grammar_score, grammar_details = self.grammar_scorer.score_sentence(
            sentence)

        # 문법 점수 기준 충족 여부 확인 및 교정
        if grammar_score < self.grammar_threshold:
            sentence = self.grammar_corrector.correct_sentence(sentence)
            grammar_score, _ = self.grammar_scorer.score_sentence(sentence)

        # 의미 일관성 점검 및 교정
        coherence_score = self.coherence_checker(sentence)
        if coherence_score < self.coherence_threshold:
            sentence = self.grammar_corrector.correct_sentence(sentence)
            coherence_score = self.coherence_checker(sentence)

        return {
            "final_sentence": sentence,
            "grammar_score": grammar_score,
            "coherence_score": coherence_score,
        }

    def process_all_sentences(self, file_path: str):
        # CSV 파일 로드
        df = pd.read_csv(file_path, encoding='cp949')
        results = []

        # 모든 문장에 대해 파이프라인 실행
        for _, row in df.iterrows():
            sentence = row["문장"]
            word = row["포함된 단어"]
            result = self.evaluate_and_correct(sentence)
            result["word"] = word
            results.append(result)

        return pd.DataFrame(results)
