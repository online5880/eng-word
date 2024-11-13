from Pipeline.sentence_pipeline import SentenceEvaluationPipeline

def main():
    # 처리할 파일 경로 설정
    file_path = 'C:/Users/user/Desktop/eng-word/utils/Grammar_Score/grammar_sentences.csv'
    
    # 파이프라인 초기화
    pipeline = SentenceEvaluationPipeline()
    
    # 모든 문장을 처리하고 결과를 출력
    results_df = pipeline.process_all_sentences(file_path)
    print("FINAL DF")
    print(results_df)


if __name__ == "__main__":
    main()
