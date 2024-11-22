import pandas as pd
import requests
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# Google Cloud Translate API 키 가져오기
api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_TRANSLATE_API_KEY가 .env 파일에 설정되지 않았습니다.")


# 번역 함수
def translate_csv(
    input_file, output_file, target_column="final_sentence", target_language="ko"
):
    # CSV 파일 로드
    df = pd.read_csv(input_file)

    # 번역 함수
    def translate_text(text, target_language="ko"):
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {"q": text, "target": target_language, "key": api_key, "source": "en"}
        try:
            response = requests.post(url, data=params)
            if response.status_code == 200:
                translated_text = response.json()["data"]["translations"][0][
                    "translatedText"
                ]
                return translated_text
            else:
                return f"번역 오류: {response.status_code}, {response.text}"
        except Exception as e:
            return f"번역 오류: {e}"

    # 새 열 추가 (번역된 문장)
    df["sentence_meaning"] = df[target_column].apply(
        translate_text, target_language=target_language
    )

    # 번역된 CSV 파일 저장
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"번역 완료. 파일이 저장되었습니다: {output_file}")
