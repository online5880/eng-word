import os
import sys
import django

from spell_stars.utils.generate.Pipeline.extract_word import extract_words
from spell_stars.utils.generate.Pipeline.generate_sentence import create_faiss_index, generate_sentences
from spell_stars.utils.generate.Pipeline.json_to_clusteredjson import assign_noise_to_nearest_cluster, cluster_words, load_words_from_json, refine_clusters_auto, save_refined_clusters_to_single_json, vectorize_words
from spell_stars.utils.generate.Pipeline.translate import translate_csv
from utils.Grammar_Score.Pipeline.sentence_pipeline import SentenceEvaluationPipeline

# Ensure we're working in the correct directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set the DJANGO_SETTINGS_MODULE to the correct path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spell_stars.settings")

# Now setup Django
django.setup()

from Pipeline.upload import Command

def main():
    # Current file location based basic path setup
    base_directory = os.path.dirname(os.path.abspath(__file__))

    # Directory paths
    pdf_directory = os.path.join(base_directory, "pdf")
    json_output_directory = os.path.join(base_directory, "json_output")
    clustered_json_path = os.path.join(base_directory, "clustered_wordbook.json")
    extracted_words_path = os.path.join(base_directory, "extracted_words.json")
    csv_output_path = os.path.join(base_directory, "generated_sentences.csv")
    vector_store_path = os.path.join(base_directory, "sentence_vectorstore")
    grammar_results_path = os.path.join(base_directory, "grammar_results.csv")
    final_sentence_path = os.path.join(base_directory, "final_sentence.csv")

    # Create necessary directories
    os.makedirs(pdf_directory, exist_ok=True)
    os.makedirs(json_output_directory, exist_ok=True)
    os.makedirs(vector_store_path, exist_ok=True)

    # Step 1: Process PDFs and convert them to JSON
    process_pdfs(pdf_directory, json_output_directory)

    # Step 2: Load JSON data, vectorize and cluster the words (this step is commented out, enable as needed)
    word_dict = load_words_from_json(json_output_directory)
    word_list = list(word_dict.keys())
    vectors = vectorize_words(word_list)
    clustered_words, noise = cluster_words(word_list, vectors, eps=0.35, min_samples=2)
    clustered_words_with_noise = assign_noise_to_nearest_cluster(clustered_words, noise)
    refined_clusters = refine_clusters_auto(clustered_words_with_noise, word_dict)
    save_refined_clusters_to_single_json(refined_clusters, clustered_json_path)

    # Step 3: Extract words from clustered JSON
    extract_words(clustered_json_path, extracted_words_path)

    # Step 4: Create FAISS index
    create_faiss_index(clustered_json_path, vector_store_path)

    # Step 5: Generate sentences based on the extracted words
    generate_sentences(extracted_words_path, vector_store_path, csv_output_path)

    # Step 6: Perform grammar check on generated sentences
    pipeline = SentenceEvaluationPipeline()
    results_df = pipeline.process_all_sentences(csv_output_path, grammar_results_path)
    results_df.to_csv(grammar_results_path, index=False, encoding="utf-8-sig")

    # Step 7: Translate the generated sentences
    translate_csv(grammar_results_path, final_sentence_path)

    # Step 8: Upload data to the database
    print("Uploading to database...")
    upload = Command()
    upload.handle(csv_file=final_sentence_path)
    print("Upload completed. Results uploaded to Sentence.")

if __name__ == "__main__":
    # Execute Django management commands
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

    # Main function execution
    main()
