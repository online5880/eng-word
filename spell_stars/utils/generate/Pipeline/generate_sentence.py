from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
import json
import csv


# llm = ChatOllama(model="Lama3.2-korean:latest", max_token = 500)
llm = ChatOllama(model="llama3.2", max_token=50, temperature=0.5)


prompt_template = PromptTemplate(
    input_variables=["query"],
    template="""
    You must create exactly one simple, complete English sentence that an elementary school student can understand.
    
    - The sentence must include the word '{query}' exactly as specified, without any modifications or additional forms.
    - Use only a single statement, not a question, command, or compound sentence.
    - The sentence should be between 5 and 8 words long.
    - Do not create multiple sentences or add any additional information.
    - Use only common, everyday words that are simple for an elementary school student in the US to understand.

    If you cannot create a sentence following these rules exactly, respond with "Unable to create a valid sentence."
    """,
)

model_name = "sentence-transformers/all-mpnet-base-v2"


# model_name = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"
hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cpu", "trust_remote_code": True},  # cuda, cpu
    encode_kwargs={"normalize_embeddings": True},
)


loaded_vector_store = FAISS.load_local(
    "./sentence_vectorstore",
    hf_embeddings,
    allow_dangerous_deserialization=True,  # 신뢰된 파일에서만 사용
)

retriever = loaded_vector_store.as_retriever()


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt_template, "document_variable_name": "query"},
)


# JSON 파일에서 단어 목록 불러오기
with open(
    r"C:\Users\user\Desktop\eng-word\spell_stars\utils\GenerateSentence_Pipeline\extracted_words.json",
    "r",
    encoding="utf-8",
) as file:
    words = json.load(file)


def main():
    # CSV 파일 생성
    with open("grammar_sentences.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["문장 번호", "문장", "포함된 단어"])

        # 각 단어에 대해 문장 생성 및 저장
        for idx, word in enumerate(words, start=1):
            response = qa_chain.invoke({"query": word})  # 체인 실행

            # response의 형식이 예상대로 되어 있는지 확인
            if "result" in response:
                generated_sentence = response["result"]

                # 문장에 포함된 단어가 정확히 있는지 검증
                if word in generated_sentence:
                    writer.writerow([idx, generated_sentence, word])
                    print(generated_sentence, word)
                else:
                    print(f"생성된 문장이 규칙을 따르지 않습니다. 단어: {word}")
            else:
                print(f"응답 형식이 잘못되었습니다. 단어: {word}")
