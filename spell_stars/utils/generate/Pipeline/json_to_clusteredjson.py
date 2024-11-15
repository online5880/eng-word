import json
import os
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from collections import Counter

# 랜덤 시드 고정
np.random.seed(42)

# Step 1: Load JSON files containing vocabulary
def load_words_from_json(directory_path):
    word_dict = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            with open(os.path.join(directory_path, filename), "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    word = item["단어"].replace("\n", "")
                    meaning = item["단어 뜻"].replace("\n", "")
                    
                    # If word is already in word_dict
                    if word in word_dict:
                        existing_item = word_dict[word]
                        
                        # Add meaning if not already present
                        if meaning not in existing_item["meanings"]:
                            existing_item["meanings"].append(meaning)
                        
                        # Add example sentences in both English and Korean
                        example = {
                            "english": item.get("예문", "").replace("\n", ""),
                            "korean": item.get("예문 뜻", "").replace("\n", "")
                        }
                        if example not in existing_item["examples"]:
                            existing_item["examples"].append(example)
                    else:
                        # Initialize new word entry
                        word_dict[word] = {
                            "meanings": [meaning],
                            "part_of_speech": item.get("품사", ""),
                            "examples": [{
                                "english": item.get("예문", "").replace("\n", ""),
                                "korean": item.get("예문 뜻", "").replace("\n", "")
                            }]
                        }
    return word_dict

# Step 2: Vectorize words
def vectorize_words(word_list):
    model = SentenceTransformer('all-mpnet-base-v2', device='cpu')  # Initialize model
    vectors = model.encode(word_list)
    return vectors

# Step 3: Cluster words using DBSCAN
def cluster_words(word_list, vectors, eps=0.35, min_samples=2):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    clusters = dbscan.fit_predict(vectors)
    
    # Store clustering results
    clustered_words = {}
    noise = []
    for idx, cluster_id in enumerate(clusters):
        if cluster_id != -1:  # If part of a cluster
            if cluster_id not in clustered_words:
                clustered_words[cluster_id] = []
            clustered_words[cluster_id].append((word_list[idx], vectors[idx]))
        else:  # If classified as noise
            noise.append((word_list[idx], vectors[idx]))
    
    return clustered_words, noise

# Step 4: Assign noise words to nearest clusters individually
def assign_noise_to_nearest_cluster(clustered_words, noise):
    if not noise:
        return clustered_words

    # Compare each noise word with clusters to find the most similar cluster
    for noise_word, noise_vector in noise:
        max_similarity = -1
        best_cluster_id = None

        # Calculate similarity with each cluster
        for cluster_id, words_with_vectors in clustered_words.items():
            cluster_vectors = np.array([vec for _, vec in words_with_vectors])
            similarities = cosine_similarity([noise_vector], cluster_vectors)
            avg_similarity = np.mean(similarities)

            # Find cluster with highest similarity
            if avg_similarity > max_similarity:
                max_similarity = avg_similarity
                best_cluster_id = cluster_id

        # Add noise word to the most similar cluster
        if best_cluster_id is not None:
            clustered_words[best_cluster_id].append((noise_word, noise_vector))
    
    return clustered_words

# Step 5: Assign categories and save refined clusters
def refine_clusters_auto(clustered_words, word_dict):
    refined_clusters = {}
    category_counts = Counter()  # Word count by category
    category_id = 0

    # Assign categories without further re-clustering
    for cluster_id, words_with_vectors in clustered_words.items():
        for word, _ in words_with_vectors:
            word_dict[word]["category"] = int(category_id)
            refined_clusters[word] = word_dict[word]
        category_counts[category_id] = len(words_with_vectors)
        category_id += 1

    # Print word count by category
    print("\nWord count by category:")
    for category, count in category_counts.items():
        print(f"Category {category}: {count} words")

    return refined_clusters

# Step 6: Save refined clusters to JSON
def save_refined_clusters_to_single_json(refined_clusters, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(refined_clusters, file, ensure_ascii=False, indent=4)

# # Execution
# directory_path = "./data"  # Path to folder with JSON files
# output_path = "./clustered_wordbook.json"  # Path to save clustered output
# word_dict = load_words_from_json(directory_path)
# word_list = list(word_dict.keys())
# vectors = vectorize_words(word_list)  # Vectorize words
# clustered_words, noise = cluster_words(word_list, vectors, eps=0.35, min_samples=2)
# clustered_words_with_noise = assign_noise_to_nearest_cluster(clustered_words, noise)
# refined_clusters = refine_clusters_auto(clustered_words_with_noise, word_dict)
# save_refined_clusters_to_single_json(refined_clusters, output_path)

# print(f"\nClustered vocabulary saved to {output_path}")
