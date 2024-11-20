import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
import json
import csv
from dotenv import load_dotenv  # .env 파일을 불러오기 위한 라이브러리
import psycopg2  # PostgreSQL 사용


# .env 파일에서 환경 변수 불러오기
load_dotenv()

# PostgreSQL에서 특정 word_id에 대한 문장 개수를 확인하는 함수
def check_word_sentence_count(word, db_params):
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # 단어에 해당하는 word_id 조회
        cursor.execute("SELECT id FROM vocab_mode_word WHERE word = %s", (word,))
        word_id = cursor.fetchone()

        if not word_id:
            print(f"단어 '{word}'에 해당하는 word_id를 찾을 수 없습니다.")
            cursor.close()
            conn.close()
            return 0  # word_id가 없으면 문장을 생성하지 않음

        word_id = word_id[0]  # word_id 추출

        # word_id에 해당하는 문장의 개수 조회
        cursor.execute("SELECT COUNT(*) FROM sent_mode_sentence WHERE word_id = %s", (word_id,))
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count
    except Exception as e:
        print(f"문장 개수 조회 중 오류 발생: {e}")
        return 0


def create_faiss_index(file_path, vector_store_path):
    try:
        # JSON 파일에서 단어 및 예문 불러오기
        with open(file_path, "r", encoding="utf-8") as file:
            word_data = json.load(file)
        print(f"JSON 파일 로드 완료: {file_path}. 단어 수: {len(word_data)}")


        example_sentences = []

        # JSON 데이터가 딕셔너리 형식이라고 가정하여 순회
        for word, entry in word_data.items():
            if "examples" in entry and entry["examples"] and isinstance(entry["examples"], list):
                for example in entry["examples"]:
                    if "english" in example:
                        example_sentences.append(example["english"])
            



        if not example_sentences:
            raise ValueError("JSON 파일에서 유효한 예문을 찾을 수 없습니다.")

        print(f"예문 생성 완료: {len(example_sentences)}개의 예문")
    except FileNotFoundError:
        print(f"JSON 파일을 찾을 수 없습니다: {file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"JSON 파일을 파싱하는 중 오류 발생: {e}")
        return
    except Exception as e:
        print(f"JSON 파일 처리 중 알 수 없는 오류 발생: {e}")
        return

    try:
        # 임베딩 모델 설정
        model_name = "sentence-transformers/all-mpnet-base-v2"
        hf_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu", "trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("임베딩 모델 로드 완료")
    except Exception as e:
        print(f"임베딩 모델 로드 중 오류 발생: {e}")
        return

    try:
        # FAISS 벡터 스토어 생성
        vector_store = FAISS.from_texts(texts=example_sentences, embedding=hf_embeddings)
        print("FAISS 벡터 스토어 생성 완료")
    except Exception as e:
        print(f"FAISS 벡터 스토어 생성 중 오류 발생: {e}")
        return

    try:
        # FAISS 벡터 스토어 저장
        os.makedirs(vector_store_path, exist_ok=True)
        vector_store.save_local(vector_store_path)
        print(f"FAISS 벡터 스토어 저장 완료: {os.path.join(vector_store_path, 'index.faiss')}")
    except Exception as e:
        print(f"FAISS 벡터 스토어 저장 중 오류 발생: {e}")
        return
    

def generate_sentences(file_path, vector_store_path, output_path):
    # LLM 설정
    llm = ChatOllama(model="llama3.2", max_token=60, temperature=0.8)

    # 프롬프트 템플릿 설정
    prompt_template = PromptTemplate(
        input_variables=["query"],
        template="""\
Your task is to create one meaningful and natural English sentence for elementary school vocabulary learning. Follow these rules carefully:

- The sentence must include the word '{query}' exactly as it is, without any changes or additional forms.
- The sentence must be clear, simple, and easy to understand for an elementary school student in the US.
- The sentence must convey a single, logical idea and remain contextually coherent.
- Keep the sentence between 6 and 10 words long.
- Use simple vocabulary and grammar that is age-appropriate and engaging for children.
- Avoid complex ideas, idioms, or culturally specific references that may confuse the learner.

If you cannot create a valid sentence under these rules, respond with: "Unable to create a valid sentence."
"""
    )

    # 단어 리스트 로드 (JSON 파일에서)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            words = json.load(file)
    except Exception as e:
        print(f"단어 파일을 로드하는 중 오류 발생: {e}")
        return

    # .env에서 PostgreSQL 연결 정보를 불러오기
    db_params = {
        "dbname": os.getenv("NAME"),
        "user": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT", 5432)  # 기본 포트 5432
    }

    # CSV 파일에 문장 생성 결과 저장
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["sentence_id", "sentence", "word"])

            # 각 단어에 대해 문장 생성 및 저장
            for idx, word in enumerate(words, start=1):
                # 단어에 대한 문장 개수 확인
                sentence_count = check_word_sentence_count(word, db_params)

                # 문장 개수가 5개 이상이면 생략
                if sentence_count >= 5:
                    print(f"단어 '{word}'에 해당하는 문장이 이미 5개 이상 존재. 문장 생성을 건너뜁니다.")
                    continue  # 해당 단어는 문장 생성하지 않음

                try:
                    # 문장 생성
                    response = llm.predict(prompt_template.format(query=word))

                    # 문장 생성 결과 확인 및 저장
                    if word in response:
                        # 문장을 DB에 저장하지 않고 CSV에만 저장
                        writer.writerow([idx, response, word])
                        print(f"Generated sentence: {response} (word: {word})")
                    else:
                        print(f"생성된 문장이 규칙을 따르지 않습니다. 단어: {word}")
                except Exception as e:
                    print(f"문장 생성 중 오류 발생. 단어: {word}, 오류: {e}")

        print(f"문장 생성 완료. 결과가 {output_path}에 저장되었습니다.")
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")