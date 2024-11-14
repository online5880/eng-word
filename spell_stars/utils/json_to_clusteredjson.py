import json
import os
import numpy as np
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer

# 랜덤 시드 고정
np.random.seed(42)


# Step 1: 단어장 JSON 파일 불러오기
def load_words_from_json(directory_path):
    word_dict = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                data = json.load(file)
                for item in data:
                    word = item["단어"]
                    meaning = item["단어 뜻"]

                    # 단어가 이미 word_dict에 있는 경우
                    if word in word_dict:
                        existing_item = word_dict[word]

                        # 단어 뜻 중복 검사 후 추가
                        if meaning not in existing_item["단어 뜻"]:
                            existing_item["단어 뜻"].append(meaning)

                        # 예문과 예문 뜻을 "영문"과 "한글" 필드로 묶어 리스트에 추가
                        example = {
                            "영문": item.get("예문", ""),
                            "한글": item.get("예문 뜻", ""),
                        }
                        if example not in existing_item["예문"]:
                            existing_item["예문"].append(example)
                    else:
                        # 새로운 단어의 경우 리스트로 초기화하여 저장
                        word_dict[word] = {
                            "단어": word,
                            "단어 뜻": [meaning],
                            "품사": item.get("품사", ""),
                            "예문": [
                                {
                                    "영문": item.get("예문", ""),
                                    "한글": item.get("예문 뜻", ""),
                                }
                            ],
                        }
    return list(word_dict.values())


# Step 2: 단어를 벡터화
def vectorize_words(word_list):
    model = SentenceTransformer("all-mpnet-base-v2", device="cpu")  # 모델 초기화
    words = [word["단어"] for word in word_list]
    vectors = model.encode(words)
    return vectors


# Step 3: DBSCAN으로 군집화
def cluster_words(word_list, vectors, eps=0.35, min_samples=2):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
    clusters = dbscan.fit_predict(vectors)

    # 클러스터링 결과 저장
    clustered_words = {}
    noise = []
    for idx, cluster_id in enumerate(clusters):
        if cluster_id != -1:  # 클러스터에 속한 경우
            if cluster_id not in clustered_words:
                clustered_words[cluster_id] = []
            clustered_words[cluster_id].append((word_list[idx], vectors[idx]))
        else:  # 노이즈로 분류된 경우
            noise.append((word_list[idx], vectors[idx]))

    return clustered_words, noise


# Step 4: 노이즈 단어를 가장 가까운 클러스터에 추가
def assign_noise_to_nearest_cluster(clustered_words, noise):
    cluster_centers = {
        cluster_id: np.mean([vec for _, vec in words], axis=0)
        for cluster_id, words in clustered_words.items()
    }

    for word_data, vec in noise:
        closest_cluster = min(
            cluster_centers.keys(),
            key=lambda c: np.linalg.norm(cluster_centers[c] - vec),
        )
        clustered_words[closest_cluster].append((word_data, vec))

    return clustered_words


# Step 5: 주제별로 세분화
def refine_clusters_auto(clustered_words):
    refined_clusters = {}
    for cluster_id, words_with_vectors in clustered_words.items():
        words = [
            word_data for word_data, _ in words_with_vectors
        ]  # 벡터를 제거하고 단어 데이터만 가져옴
        topic_name = f"category_{cluster_id}"  # 자동으로 생성된 주제명
        refined_clusters[topic_name] = words
    return refined_clusters


# Step 6: JSON 파일로 저장
def save_refined_clusters_to_single_json(refined_clusters, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(refined_clusters, file, ensure_ascii=False, indent=4)


# 실행
directory_path = "./data"  # JSON 파일들이 있는 폴더 경로 설정
output_path = "./clustered_wordbook.json"  # 군집화 결과를 저장할 파일 경로 설정
word_list = load_words_from_json(directory_path)
vectors = vectorize_words(word_list)  # 단어 자체를 벡터화
clustered_words, noise = cluster_words(word_list, vectors, eps=0.35, min_samples=2)
clustered_words_with_noise = assign_noise_to_nearest_cluster(clustered_words, noise)
refined_clusters = refine_clusters_auto(clustered_words_with_noise)


save_refined_clusters_to_single_json(refined_clusters, output_path)
