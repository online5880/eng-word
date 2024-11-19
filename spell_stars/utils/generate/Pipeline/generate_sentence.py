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
    

def generate_sentences(file_path, vector_store_path, output_path, num_sentences_per_word=5):
    # LLM 설정
    llm = ChatOllama(model="llama3.2", max_token=50, temperature=0.9, top_p=0.9)

    # 프롬프트 템플릿 설정
    prompt_template = PromptTemplate(
        input_variables=["query"],
        template="""
        Create one clear, meaningful sentence using the word '{query}' exactly as it is.

        Rules:
        - The sentence must be a single declarative sentence.
        - It must include the word '{query}' without changes or additional forms.
        - The sentence should be between 6 and 8 words long.
        - Use simple words suitable for elementary school students.

        If a valid sentence cannot be created, respond with: "Unable to create a valid sentence."
        """
    )

    # FAISS 벡터 스토어 로드
    vector_store = FAISS.load_local(vector_store_path, HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={"device": "cpu", "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True}
    ), allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever()
    print("FAISS 벡터 스토어 로드 및 리트리버 생성 완료.")

    # QA 체인 설정
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template, "document_variable_name": "query"},
    )
    print("QA 체인 설정 완료.")

    # 단어 리스트 로드
    with open(file_path, "r", encoding="utf-8") as file:
        words = list(json.load(file))

    # CSV 파일에 문장 생성 결과 저장
    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sentence_id", "sentence", "word"])

        # 각 단어에 대해 다수의 문장 생성
        for idx, word in enumerate(words, start=1):
            generated_sentences = set()  # 중복 방지를 위한 집합

            for attempt in range(num_sentences_per_word * 2):  # 최대 시도 횟수
                response = qa_chain.invoke({"query": word})
                generated_sentence = response.get("result", "").strip()

                # 문장 검증: 규칙 확인 및 중복 방지
                if (word in generated_sentence
                        and generated_sentence.count(".") == 1
                        and generated_sentence not in generated_sentences):
                    generated_sentences.add(generated_sentence)
                    writer.writerow([f"{idx}-{len(generated_sentences)}", generated_sentence, word])
                    print(f"Generated sentence {len(generated_sentences)} for '{word}': {generated_sentence}")

                # 지정된 문장 개수 충족 시 중단
                if len(generated_sentences) >= num_sentences_per_word:
                    break

            if len(generated_sentences) < num_sentences_per_word:
                print(f"Warning: Only {len(generated_sentences)} sentences generated for word '{word}'")

    print(f"문장 생성 완료. 결과가 {output_path}에 저장되었습니다.")
