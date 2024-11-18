import csv
from django.core.management.base import BaseCommand
import os
import sys

sys.path.append(os.path.abspath('C:/Users/user/Desktop/eng_word/spell_stars'))

from sent_mode.models import Sentence
from vocab_mode.models import Word


class Command(BaseCommand):
    help = "CSV 파일 데이터를 Sentence 모델에 적재합니다."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="CSV 파일 경로")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        try:
            with open(csv_file, newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # CSV 데이터 확인
                    print(f"Processing row: {row}")

                    word_name = row["word"]  # CSV 파일에서 단어 이름 읽기
                    sentence = row["final_sentence"]
                    sentence_meaning = row["sentence_meaning"]

                    # final_sentence가 존재하는지 확인
                    if not sentence:
                        self.stdout.write(
                            self.style.WARNING(f"final_sentence가 없습니다: {row}")
                        )
                        continue  # final_sentence가 없으면 건너뜁니다.

                    # Word 모델에서 단어 이름으로 조회
                    try:
                        print(f"Looking for Word: {word_name}")  # 디버깅: 단어 찾기 전에 로그
                        word = Word.objects.get(word=word_name)
                    except Word.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"단어 '{word_name}'가 Word 테이블에 존재하지 않습니다."
                            )
                        )
                        continue  # 단어가 없으면 건너뜁니다.

                    # 이미 존재하는 Sentence인지 확인
                    if Sentence.objects.filter(word=word, sentence=sentence).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f"Sentence '{sentence}'는 이미 존재합니다. 건너뜁니다."
                            )
                        )
                        continue  # 이미 존재하면 건너뜁니다.

                    # Sentence 모델에 데이터 저장
                    try:
                        print(f"Saving Sentence: {sentence}")  # 디버깅: 저장 전 로그
                        Sentence.objects.create(
                            word=word,  # 외래 키로 저장
                            sentence=sentence,
                            sentence_meaning=sentence_meaning,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f"Sentence '{sentence}' 저장 성공")
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Sentence 저장 중 오류 발생: {e}"))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"파일 {csv_file}을(를) 찾을 수 없습니다.")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"오류 발생: {e}"))
