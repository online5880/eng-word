import os
from Pipeline.pdf_to_json import process_pdfs
from Pipeline.json_to_clusteredjson import load_words_from_json, vectorize_words, cluster_words, assign_noise_to_nearest_cluster, refine_clusters_auto, save_refined_clusters_to_single_json
from Pipeline.extract_word import extract_words
from Pipeline.generate_sentence import generate_sentences

# Step 1: Define paths
pdf_directory = "./pdf"  # Folder containing PDF files to process
json_output_directory = "./json_output"  # Folder to store JSON files after PDF processing
clustered_json_path = "./clustered_wordbook.json"  # Path for the clustered JSON output
extracted_words_path = "./extracted_words.json"  # Path for extracted words JSON
csv_output_path = "generated_sentences.csv"  # Path for generated sentences CSV

# Step 2: Convert PDF files to JSON
print("Starting PDF to JSON conversion...")
process_pdfs(pdf_directory, json_output_directory)

# Step 3: Load and cluster JSON data
print("Starting JSON clustering...")
word_dict = load_words_from_json(json_output_directory)
word_list = list(word_dict.keys())
vectors = vectorize_words(word_list)
clustered_words, noise = cluster_words(word_list, vectors, eps=0.35, min_samples=2)
clustered_words_with_noise = assign_noise_to_nearest_cluster(clustered_words, noise)
refined_clusters = refine_clusters_auto(clustered_words_with_noise, word_dict)
save_refined_clusters_to_single_json(refined_clusters, clustered_json_path)

# Step 4: Extract words from clustered JSON
print("Extracting words from clustered JSON...")
extract_words(clustered_json_path, extracted_words_path)

# Step 5: Generate sentences for extracted words
print("Generating sentences from extracted words...")
generate_sentences(extracted_words_path, csv_output_path)

print("Pipeline completed successfully! Check the outputs in the specified directories.")
