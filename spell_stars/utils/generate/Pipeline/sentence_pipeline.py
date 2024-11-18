import pandas as pd
from Pipeline.grammar_score import AdvancedGrammarScorer  # 문법 검사 클래스
from Pipeline.consistency import measure_sc  # 의미 일관성 검사 함수
from Pipeline.grammar_corrector import GrammarCorrector # Grammarformer를 사용한 문장 보완 클래스
import chardet


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
        grammar_score, grammar_details = self.grammar_scorer.score_sentence(sentence)

        # 문법 점수 기준 충족 여부 확인 및 교정
        if grammar_score < self.grammar_threshold:
            corrected_sentence = self.grammar_corrector.correct_sentence(sentence)
            
            # 중복 확인: 수정된 문장이 원래 문장과 같다면 더 이상 수정하지 않음
            if corrected_sentence != sentence:
                sentence = corrected_sentence
                grammar_score, _ = self.grammar_scorer.score_sentence(sentence)

        # 의미 일관성 점검 및 교정
        coherence_score = self.coherence_checker(sentence)
        if coherence_score < self.coherence_threshold:
            corrected_sentence = self.grammar_corrector.correct_sentence(sentence)
            
            # 중복 확인: 수정된 문장이 원래 문장과 같다면 더 이상 수정하지 않음
            if corrected_sentence != sentence:
                sentence = corrected_sentence
                coherence_score = self.coherence_checker(sentence)

        return {
            "final_sentence": sentence,
            "grammar_score": grammar_score,
            "coherence_score": coherence_score,
        }

    def process_all_sentences(self, file_path: str):
        # 파일의 인코딩 감지
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        # 감지된 인코딩으로 CSV 파일 로드
        df = pd.read_csv(file_path, encoding=encoding)

        results = []

        # 모든 문장에 대해 파이프라인 실행
        for _, row in df.iterrows():
            # 비문자열 데이터를 문자열로 변환하고 NaN 값은 빈 문자열로 대체
            sentence = str(row["sentence"]) if pd.notnull(row["sentence"]) else ""
            word = str(row["word"]) if pd.notnull(row["word"]) else ""

            # 문장 평가 및 수정
            result = self.evaluate_and_correct(sentence)
            result["word"] = word
            results.append(result)

        return pd.DataFrame(results)