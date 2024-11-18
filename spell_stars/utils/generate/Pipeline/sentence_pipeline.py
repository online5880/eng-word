import pandas as pd
from Pipeline.grammar_score import AdvancedGrammarScorer  # 문법 검사 클래스
from Pipeline.consistency import measure_sc  # 의미 일관성 검사 함수
from Pipeline.grammar_corrector import (
    GrammarCorrector,
)  # Grammarformer를 사용한 문장 보완 클래스
import chardet
from concurrent.futures import ThreadPoolExecutor
import time


class SentenceEvaluationPipeline:

    def __init__(
        self,
        grammar_threshold: float = 0.95,
        coherence_threshold: int = 1,
        batch_size=10,
        max_workers=2,
    ):  # 병렬 처리 워커 수 추가
        self.grammar_scorer = AdvancedGrammarScorer()  # 문법 점수 측정
        self.coherence_checker = measure_sc  # 의미 일관성 점검 함수
        self.grammar_threshold = grammar_threshold  # 문법 점수 기준
        self.coherence_threshold = coherence_threshold  # 일관성 기준
        self.grammar_corrector = GrammarCorrector()  # GrammarCorrector 초기화
        self.batch_size = batch_size  # 배치 크기
        self.max_workers = max_workers  # 병렬 처리 워커 수

    def evaluate_and_correct(self, sentence: str):
        start_time = time.time()
        try:
            # 원본 문장
            original_sentence = sentence

            # 문법 점수 계산
            grammar_score, grammar_details = self.grammar_scorer.score_sentence(
                sentence
            )

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
            end_time = time.time()
            print(f"Processed sentence in {end_time - start_time:.2f} seconds.")
            return {
                "final_sentence": sentence,
                "grammar_score": grammar_score,
                "coherence_score": coherence_score,
            }
        except Exception as e:
            print(f"Error processing sentence: {sentence[:50]}... Error: {e}")
            return {
                "final_sentence": sentence,
                "grammar_score": 0,
                "coherence_score": 0,
                "error": str(e),
            }

    def process_batch(self, batch):
        batch_results = []
        for i, row in batch.iterrows():
            sentence = str(row["sentence"]) if pd.notnull(row["sentence"]) else ""
            word = str(row["word"]) if pd.notnull(row["word"]) else ""

            # 문장 평가 및 수정
            start_time = time.time()
            result = self.evaluate_and_correct(sentence)
            print(
                f"Sentence {i} evaluation time: {time.time() - start_time:.2f} seconds"
            )

            result["word"] = word
            batch_results.append(result)
        return batch_results

    def process_all_sentences(self, file_path: str, output_path: str):
        # 파일의 인코딩 감지
        with open(file_path, "rb") as f:
            result = chardet.detect(f.read())
            encoding = result["encoding"]

        # 감지된 인코딩으로 CSV 파일 로드
        df = pd.read_csv(file_path, encoding=encoding)

        total_results = []
        num_sentences = len(df)

        # 배치 단위로 문장 처리 (병렬 처리)
        print("Starting parallel processing...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for start_idx in range(0, num_sentences, self.batch_size):
                end_idx = min(start_idx + self.batch_size, num_sentences)
                batch = df.iloc[start_idx:end_idx]
                print(f"Queuing batch {start_idx + 1} to {end_idx}...")
                futures.append(executor.submit(self.process_batch, batch))

            for future in futures:
                batch_results = future.result()
                total_results.extend(batch_results)

        # 전체 결과를 DataFrame으로 저장
        results_df = pd.DataFrame(total_results)
        results_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"All sentences processed. Results saved to {output_path}")

        return results_df
