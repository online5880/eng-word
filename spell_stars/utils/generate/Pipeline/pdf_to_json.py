#  최종 코드
import pdfplumber
import fitz  # PyMuPDF
import os
import re
import json

def extract_lesson_titles(page): # 페이지에서 "Lesson" 제목을 추출하는 함수
    text = page.extract_text()  # 페이지의 텍스트를 추출
    lesson_titles = re.findall(r'Lesson \d+\. (.+?)\s*\n', text)  # "Lesson" 번호와 제목을 정규식으로 찾음
    return lesson_titles

def extract_data_from_table(row): # 테이블의 행에서 예문과 예문 뜻을 분리하는 함수
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
    
    # 예문과 예문 뜻에서 한국어 문장이 섞여 있는 경우 처리
    if example_meaning.startswith('씨'):
        concat = example_sentence + example_meaning
        example_meaning = extract_sentences_with_korean(concat)[0]
        example_sentence = concat.replace(example_meaning, '')
    
    if len(mixed) > 0: 
        if mixed[0] in example_sentence:
            example_sentence = example_sentence.replace(mixed[0], '')
            example_meaning = mixed[0] + ' ' + example_meaning

    # 품사와 단어 뜻을 정규식으로 추출
    pos_match = re.search(r'(\w+)\)\s*', row[3])
    if pos_match:
        part_of_speech = pos_match.group(1)  # 품사 추출
        meaning_text = re.sub(r'\s*\(\w+\)\s*', '', row[3]).strip()  # 뜻에서 품사 제거
    else:
        part_of_speech = ""
        meaning_text = row[3].strip()

    # 반환할 단어 정보 사전 생성
    return {
        "단어": remove_newlines(row[0].strip()),
        "단어 뜻": meaning_text.replace(part_of_speech + ')', '').strip(),
        "품사": part_of_speech,
        "예문": example_sentence.strip(),
        "예문 뜻": example_meaning.strip(),
    }

def remove_newlines(text):  # 문자열에서 개행 문자를 제거하는 함수
    return text.replace("\n", " ").replace("\r", "")

def extract_sentences_with_korean(text):  # 영문장에서 한국어가 존재시 재 추출하는 함수
    sentences = re.split(r'(?<=[.?!])\s+', text)
    korean_sentences = [sentence for sentence in sentences if re.search(r'[가-힣]', sentence)]
    return korean_sentences

def safe_filename(filename):  # 파일 이름에서 안전하지 않은 문자를 제거하는 함수
    return re.sub(r'[\/\:*?"<>|]', "", filename)

def pdf_to_json(pdf_path, output_directory):  # beyond.pdf를 제외한 pdf용 : pdfplumber를 사용하여 PDF를 JSON으로 변환하는 함수
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
            # print(f"Parsed data for {pdf_path} page {page_number + 1}:", data)

def clean_text(text):  # 텍스트의 양끝 공백을 제거하는 함수
    return text.strip()

def format_sentence(sentence):  # 예문 형식을 정리하는 함수
    if re.search(r'\s햄', sentence):
        sentence = sentence.replace(".  햄", "\n햄")
    return sentence

def extract_words_from_pdf_by_page(pdf_path, output_dir="output_pages"):  # beyond.pdf용 : PyMuPDF를 사용하여 페이지별로 PDF 단어를 추출하는 함수
    document = fitz.open(pdf_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text = format_sentence(page.get_text().replace('"', '')).replace(". 나", "\n나").replace("\n는", "는").replace(". 우", "\n우").replace("\n만", "만").replace("\n다", "다")
        text = text.replace("\n있다", "있다").replace("\n은편에", "은편에").replace('다음', '\n다음').replace('만년설이', '\n만년설이').replace('다른', '\n다른')
        text = text.replace('그는 친절하지만', '\n그는 친절하지만').replace('그녀는 정말', '\n그녀는 정말').replace('추신으로', '\n추신으로').replace('다이어트','\n다이어트')
        text = text.replace('금속은', '\n금속은').replace('\nDecember', 'December').replace('동물에','\n동물에').replace('\n과외의','과외의').replace('\n이외의', '이외의')
        text = text.replace('남극의', '\n남극의').replace('\ninsisted','insisted').replace('\nchild','child').replace('\n을 걱정하다', '을 걱정하다').replace('\n구성되어 있다','구성되어 있다').replace('\n하다','하다')
        text = text.replace('그 경주에는', '\n그 경주에는').replace('그는 교사이자','\n그는 교사이자').replace('\nproblem.','problem.').replace('\n동물에', '동물에').replace('그녀는 즐','\n그녀는 즐')
        text = text.replace('\nclass', 'class').replace('\nstudents.', 'students.').replace('학습 환경은', '\n학습 환경은').replace('\n다른 의견을', '다른 의견을').replace('classic', '\nclassic')
        text = text.replace('\nclassic film', 'classic film').replace('\n주 귀중한','주 귀중한').replace('문 손잡이를','\n문 손잡이를').replace('classify','\nclassify').replace('\nclassify the books','classify the books')
        text = text.replace('\n다음 주까지', '다음 주까지').replace('동물에', '\n동물에').replace('후식', '\n후식').replace('\n조금/약간', '조금/약간').replace('\n있는', '있는').replace('a little', 'a_little')
        
        # Lesson 제목을 뽑아서 파일 이름에 포함
        lesson_title = re.search(r'Lesson \d+\. (.+?)\s*\n', text)
        title_text = lesson_title.group(1) if lesson_title else f"Page_{page_num + 1}"
        safe_title_text = safe_filename(title_text)

        # 단어 정보 추출 패턴 정의
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
        
        # JSON 파일 저장
        output_file = os.path.join(output_dir, f"{os.path.basename(pdf_path).replace('.pdf', '')}_page_{page_num + 1}_{safe_title_text}.json")
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(page_words, json_file, ensure_ascii=False, indent=4)



def process_pdfs(pdf_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    for pdf_file in os.listdir(pdf_directory):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        if pdf_file.endswith(".pdf"):
            if pdf_file == "T9EE70U04.pdf":
                print(f"{pdf_file}를 처리하는 중...")
                extract_words_from_pdf_by_page(pdf_path, output_dir=output_directory)
            else:
                pdf_to_json(pdf_path, output_directory)

# # 디렉토리 설정
# pdf_directory = "./json_words/pdf" # PDF 경로
# output_directory = "./json_words/data" # 변환된 json들이 들어갈 폴더

# # PDF 파일 처리
# process_pdfs(pdf_directory, output_directory)