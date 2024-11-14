import json

file_path = r"C:\Users\user\Desktop\eng-word\utils\json_words\clustered_wordbook.json"
with open(file_path, encoding="utf-8") as file:
    data = json.load(file)

data

################################################################################################################################################################################################################

words = [entry["단어"] for category in data.values() for entry in category]
words

output_path = "./extracted_words.json"
with open(output_path, "w", encoding="utf-8") as File:
    json.dump(words, File, ensure_ascii=False, indent=4)
