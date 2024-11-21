import json

def extract_words(file_path, output_path):
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)

    # 단어 추출 (JSON의 최상위 키)
    words = list(data.keys())

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=4)

    print("Words have been extracted and saved to", output_path)
