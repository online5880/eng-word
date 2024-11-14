import pdfplumber
import fitz  # PyMuPDF
import os
import re
import json

def extract_lesson_titles(page):
    """
    페이지에서 "Lesson" 제목을 추출하는 함수

    파라미터:
        page (pdfplumber.page.Page): PDF의 특정 페이지를 나타내는 객체.

    반환값:
        list: 페이지에서 추출된 "Lesson" 제목의 리스트.
    """
    text = page.extract_text()  # 페이지의 텍스트를 추출
    lesson_titles = re.findall(r'Lesson \d+\. (.+?)\s*\n', text)  # "Lesson" 번호와 제목을 정규식으로 찾음
    return lesson_titles

def extract_data_from_table(row):
    """
    테이블의 행(row)에서 예문과 예문 뜻을 분리하여 단어 정보를 추출하는 함수

    파라미터:
        row (list): PDF 테이블의 행 데이터를 나타내는 리스트.

    반환값:
        dict: 단어, 단어 뜻, 품사, 예문, 예문 뜻을 포함하는 단어 정보 딕셔너리.
    """
    example_sentence, example_meaning = "", ""
    if re.search(r'[A-Za-z]+.*?[.!?]\s+[가-힣]', row[6]):  # 영어와 한글이 섞인 패턴을 찾음
        parts = re.split(r'(?<=[.!?])\s+(?=[가-힣])', row[6], 1)  # 영어 문장과 한글 뜻을 분리
    elif re.search(r'[A-Za-z]+\s+[가-힣]', row[6]):
        parts = re.split(r'(?<=[A-Za-z])\s+(?=[가-힣])', row[6], 1)  # 영어 단어와 한글 뜻을 분리
    elif "\n" in row[6]:
        parts = row[6].split("\n", 1)  # 개행으로 구분된 경우 분리
    else:
        parts = [row[6].strip(), ""]  # 기본적으로 공백 제거 후 할당

    example_sentence = remove_newlines(parts[0].strip())  # 예문에서 개행 제거
    mixed = extract_sentences_with_korean(example_sentence)  # 예문에서 한국어 문장을 추출
    example_meaning = remove_newlines(parts[1].strip()) if len(parts) > 1 else ""  # 예문 뜻에서 개행 제거
    
    # 품사와 단어 뜻을 정규식으로 추출
    pos_match = re.search(r'(\w+)\)\s*', row[3])
    if pos_match:
        part_of_speech = pos_match.group(1)  # 품사 추출
        meaning_text = re.sub(r'\s*\(\w+\)\s*', '', row[3]).strip()  # 뜻에서 품사 제거
    else:
        part_of_speech = ""
        meaning_text = row[3].strip()

    return {
        "단어": remove_newlines(row[0].strip()),
        "단어 뜻": meaning_text.replace(part_of_speech + ')', '').strip(),
        "품사": part_of_speech,
        "예문": example_sentence.strip(),
        "예문 뜻": example_meaning.strip(),
    }

def remove_newlines(text):
    """
    문자열에서 개행 문자를 제거하는 함수

    파라미터:
        text (str): 개행을 제거할 문자열.

    반환값:
        str: 개행이 제거된 문자열.
    """
    return text.replace("\n", " ").replace("\r", "")

def extract_sentences_with_korean(text):
    """
    영문장에서 한국어가 포함된 문장만 추출하는 함수

    파라미터:
        text (str): 분석할 텍스트 문자열.

    반환값:
        list: 한국어 문장이 포함된 문장의 리스트.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    korean_sentences = [sentence for sentence in sentences if re.search(r'[가-힣]', sentence)]
    return korean_sentences

def safe_filename(filename):
    """
    파일 이름에서 안전하지 않은 문자를 제거하는 함수

    파라미터:
        filename (str): 파일 이름 문자열.

    반환값:
        str: 파일 이름으로 안전하게 사용할 수 있도록 특수 문자가 제거된 문자열.
    """
    return re.sub(r'[\/\:*?"<>|]', "", filename)

def pdf_to_json(pdf_path, output_directory):
    """
    PDF 파일을 읽어 각 페이지의 "Lesson" 제목과 단어 정보를 JSON 파일로 변환하는 함수 (pdfplumber 사용)

    파라미터:
        pdf_path (str): 변환할 PDF 파일의 경로.
        output_directory (str): JSON 파일을 저장할 출력 디렉토리 경로.
    """
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            lesson_titles = extract_lesson_titles(page)  # "Lesson" 제목 추출
            title_text = " - ".join(lesson_titles)  # 제목을 파일명으로 변환
            safe_title_text = safe_filename(title_text)  # 안전한 파일명 변환
            data = []
            tables = page.extract_tables()  # 페이지에서 테이블 추출
            for table in tables:
                for row in table:
                    if len(row) > 0:
                        entry = extract_data_from_table(row)  # 테이블 행을 데이터로 변환
                        if any(entry.values()):
                            data.append(entry)
            # JSON 파일로 저장
            output_file = os.path.join(output_directory, f"{os.path.basename(pdf_path).replace('.pdf', '')}_page_{page_number + 1}_{safe_title_text}.json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Parsed data for {pdf_path} page {page_number + 1}:", data)

def clean_text(text):
    """
    텍스트의 양끝 공백을 제거하는 함수

    파라미터:
        text (str): 공백을 제거할 텍스트 문자열.

    반환값:
        str: 양끝의 공백이 제거된 텍스트.
    """
    return text.strip()

def format_sentence(sentence):
    """
    예문 형식을 정리하는 함수

    파라미터:
        sentence (str): 형식을 정리할 예문 문자열.

    반환값:
        str: 형식이 정리된 예문 문자열.
    """
    if re.search(r'\s햄', sentence):
        sentence = sentence.replace(".  햄", "\n햄")
    return sentence

def extract_words_from_pdf_by_page(pdf_path, output_dir="output_pages"):
    """
    PDF 파일(beyond.pdf)을 페이지별로 처리하여 단어 정보를 JSON 파일로 추출하는 함수 (PyMuPDF 사용)

    파라미터:
        pdf_path (str): 처리할 PDF 파일의 경로.
        output_dir (str): JSON 파일을 저장할 출력 디렉토리 경로.
    """
    document = fitz.open(pdf_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text = format_sentence(page.get_text().replace('"', ''))  
        lesson_title = re.search(r'Lesson \d+\. (.+?)\s*\n', text)
        title_text = lesson_title.group(1) if lesson_title else f"Page_{page_num + 1}"
        safe_title_text = safe_filename(title_text)

        pattern = r"(?P<단어>\w+)\s+(?P<품사>[a-z.]+)\s+(?P<단어_뜻>.+?)\n(?P<예문>.+?)\n(?P<예문_뜻>.+?)\n"
        if page_num == 12 or page_num == 23:
            pattern = r"(?P<단어>\w+(?:\s\w+)*)\s+(?P<품사>[a-z.]+)\s+(?P<단어_뜻>.+?)\n(?P<예문>.+?)\n(?P<예문_뜻>.+?)\n"
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        page_words = []
        for match in matches:
            word_info = {
                "단어": clean_text(match.group("단어")),
                "단어 뜻": clean_text(match.group("단어_뜻")),
                "품사": clean_text(match.group("품사")),
                "예문": clean_text(match.group("예문")),
                "예문 뜻": clean_text(match.group("예문_뜻"))
            }
            if word_info["단어"] and word_info["예문"]:
                page_words.append(word_info)
        
        output_file = os.path.join(output_dir, f"{os.path.basename(pdf_path).replace('.pdf', '')}_page_{page_num + 1}_{safe_title_text}.json")
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(page_words, json_file, ensure_ascii=False, indent=4)

def process_pdfs(pdf_directory, output_directory):
    """
    지정된 디렉토리 내의 PDF 파일들을 처리하여 JSON 파일로 저장하는 함수

    파라미터:
        pdf_directory (str): PDF 파일들이 위치한 디렉토리 경로.
        output_directory (str): JSON 파일을 저장할 출력 디렉토리 경로.
    """
    os.makedirs(output_directory, exist_ok=True)
    for pdf_file in os.listdir(pdf_directory):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        if pdf_file.endswith(".pdf"):
            if pdf_file == "beyond.pdf":
                print(f"{pdf_file}를 처리하는 중...")
                extract_words_from_pdf_by_page(pdf_path, output_dir=output_directory)
            else:
                pdf_to_json(pdf_path, output_directory)
