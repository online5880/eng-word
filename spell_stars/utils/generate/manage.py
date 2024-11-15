import os
from Pipeline.pdf_to_json import process_pdfs
from Pipeline.json_to_clusteredjson import load_words_from_json, vectorize_words, cluster_words, assign_noise_to_nearest_cluster, refine_clusters_auto, save_refined_clusters_to_single_json
from Pipeline.extract_word import extract_words
from Pipeline.generate_sentence import create_faiss_index, generate_sentences

# 현재 파일 위치 기반 기본 경로 설정
base_directory = os.path.dirname(os.path.abspath(__file__))

# 경로 설정
pdf_directory = os.path.join(base_directory, "pdf")  # PDF 파일 폴더
json_output_directory = os.path.join(base_directory, "json_output")  # JSON 파일 저장 폴더
clustered_json_path = os.path.join(base_directory, "clustered_wordbook.json")  # 군집화된 JSON 출력 경로
extracted_words_path = os.path.join(base_directory, "extracted_words.json")  # 추출된 단어 JSON 경로
csv_output_path = os.path.join(base_directory, "generated_sentences.csv")  # 생성된 문장 CSV 경로
vector_store_path = os.path.join(base_directory, "sentence_vectorstore")  # FAISS 인덱스 저장 경로

# 필요한 디렉토리 생성
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(json_output_directory, exist_ok=True)
os.makedirs(vector_store_path, exist_ok=True)  # FAISS 디렉토리 생성

# Step 1: PDF 파일을 JSON으로 변환
print("Starting PDF to JSON conversion...")
process_pdfs(pdf_directory, json_output_directory)

# Step 2: JSON 데이터를 로드하고 클러스터링
print("Starting JSON clustering...")
word_dict = load_words_from_json(json_output_directory)
word_list = list(word_dict.keys())
vectors = vectorize_words(word_list)
clustered_words, noise = cluster_words(word_list, vectors, eps=0.35, min_samples=2)
clustered_words_with_noise = assign_noise_to_nearest_cluster(clustered_words, noise)
refined_clusters = refine_clusters_auto(clustered_words_with_noise, word_dict)
save_refined_clusters_to_single_json(refined_clusters, clustered_json_path)

# Step 3: 군집화된 JSON에서 단어 추출
print("Extracting words from clustered JSON...")
extract_words(clustered_json_path, extracted_words_path)

# Step 4: FAISS 인덱스 생성
print("Creating FAISS index...")
create_faiss_index(clustered_json_path, vector_store_path)

# Step 5: 추출된 단어로 문장 생성
print("Generating sentences from extracted words...")
generate_sentences(extracted_words_path, vector_store_path, csv_output_path)

print("Pipeline completed successfully! Check the outputs in the specified directories.")
