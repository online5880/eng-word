from Pipeline.sentence_pipeline import SentenceEvaluationPipeline

def main():
    # 처리할 파일 경로 설정
    file_path = 'C:/Users/user/Desktop/eng-word/utils/Grammar_Score/grammar_sentences.csv'
    
    # 파이프라인 초기화
    pipeline = SentenceEvaluationPipeline()
    
    # 모든 문장을 처리하고 결과를 출력
    results = pipeline.process_all_sentences(file_path)
    for res in results:
        print("\nProcessed Result:")
        print("Word:", res["word"])
        print("Final Sentence:", res["final_sentence"])
        print("Final Grammar Score:", res["grammar_score"])
        print("Final Coherence Score:", res["coherence_score"])

if __name__ == "__main__":
    main()
