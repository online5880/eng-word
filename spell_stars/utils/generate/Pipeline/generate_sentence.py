import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
import json
import csv



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

    # 단어 리스트 로드
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            words = json.load(file)
    except Exception as e:
        print(f"단어 파일을 로드하는 중 오류 발생: {e}")
        return

    # CSV 파일에 문장 생성 결과 저장
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["sentence_id", "sentence", "word"])

            # 각 단어에 대해 문장 생성 및 저장
            for idx, word in enumerate(words, start=1):
                try:
                    response = llm.predict(prompt_template.format(query=word))

                    # 문장 생성 결과 확인 및 저장
                    if word in response:
                        writer.writerow([idx, response, word])
                        print(f"Generated sentence: {response} (word: {word})")
                    else:
                        print(f"생성된 문장이 규칙을 따르지 않습니다. 단어: {word}")
                except Exception as e:
                    print(f"문장 생성 중 오류 발생. 단어: {word}, 오류: {e}")

        print(f"문장 생성 완료. 결과가 {output_path}에 저장되었습니다.")
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")