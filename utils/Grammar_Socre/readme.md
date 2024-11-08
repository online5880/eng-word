# 문법 품질 점수 측정

## 용도

- LLM이 생성한 문법의 오류를 0~1사이의 점수로 수치화하기 위함.

## 패키지

## 사용된 패키지

1. **spaCy**

   - **설명**: 자연어 처리를 위한 고성능 라이브러리로, 텍스트에서 토큰화, 품사 태깅, 의존 구문 분석 등의 작업을 쉽게 수행할 수 있습니다.
   - **사용한 모듈**: `spacy`

2. **Transformers**

   - **설명**: Hugging Face에서 제공하는 사전 학습된 언어 모델 라이브러리로, BERT, GPT-2, RoBERTa 등 다양한 Transformer 모델을 사용할 수 있습니다.
   - **사용한 모듈**: `BertForSequenceClassification`, `BertTokenizer`
   - **주요 역할**: 문법 오류 탐지를 위한 BERT 기반 문장 분류 모델을 로드하고, 텍스트 토큰화를 수행합니다.

3. **Typing**

   - **설명**: Python의 정적 타입 힌팅을 위한 표준 라이브러리로, 타입을 명시하여 코드의 가독성과 안정성을 높입니다.
   - **사용한 모듈**: `Dict`, `Tuple`

4. **re (Regular Expressions)**

   - **설명**: 정규 표현식을 사용하여 텍스트 내 특정 패턴을 찾거나, 텍스트 패턴을 조작할 수 있습니다.
   - **사용한 모듈**: `re`
   - **주요 역할**: 반복적인 문자 패턴이나 특정 형식의 텍스트를 감지하여 문법 오류를 감지할 때 사용됩니다.

5. **collections**
   - **설명**: Python 표준 라이브러리의 컬렉션 모듈로, 고급 데이터 구조를 제공합니다.
   - **사용한 모듈**: `Counter`
   - **주요 역할**: 텍스트에서 단어의 출현 빈도를 계산하여, 반복되는 단어나 특정 패턴을 감지하는 데 사용됩니다.

## 기능

> 각 검사를 거친 후 각 지표의 값의 평균을 내어 점수화

### 1. 입력 문장 전처리

- **처리 내용**: `doc = self.nlp(sentence)`을 통해 `sentence` 문장을 SpaCy의 NLP 파이프라인으로 전처리하여, 각 토큰에 대한 품사 태그, 의존 관계, 어휘 정보 등을 분석합니다.
- **이유**: 의존 구문 분석(Dependency Parsing)을 통해 주어와 동사 관계, 문장 구조 복잡성 등을 평가할 수 있습니다.
- **연구적 근거**: SpaCy와 같은 NLP 파이프라인을 사용하여 문장 구문을 분석하고 오류를 탐지하는 방법은 널리 사용되며, 문법적 구조 분석을 통해 더 정확한 오류 감지가 가능하다는 연구들이 있습니다 [[1]](#1).

### 2. 기본 검사 (Basic Checks)

- **처리 내용**: 문장의 시작이 대문자인지(`starts_with_capital`), 문장이 `.` 또는 `!`, `?`로 끝나는지(`ends_with_punctuation`), 그리고 이중 문장부호가 없는지(`no_multiple_punctuation`)를 검사합니다.
- **이유**: 간단한 문법 오류는 기본적인 형식 체크만으로도 감지할 수 있습니다. 특히 대문자 시작과 올바른 종결 문장 부호 사용은 문법적 오류 여부를 쉽게 확인할 수 있습니다.
- **연구적 근거**: 형식 기반 검사(basic form check)는 초급 수준의 오류 감지에 효과적입니다 [[2]](#2).

### 3. 문장 구조 검사 (Sentence Structure Check)

- **처리 내용**: 주어(`has_subject`), 동사(`has_verb`), 주어-동사 일치 여부(`verb_agreement`)를 검사합니다.
- **이유**: 주어와 동사는 문장 구성의 핵심 요소이며, 주어와 동사 간의 일치가 중요합니다. 이를 통해 기본적인 문장 구조 오류를 감지할 수 있습니다.
- **연구적 근거**: 주어와 동사 간의 일치는 문법적 일관성을 유지하기 위한 필수 요소입니다. 연구에 따르면, 이러한 구조적 요소의 결함은 주요 문법 오류의 원인이 됩니다 [[3]](#3).

### 4. 단어 수 검사 (Word Count Check)

- **처리 내용**: 문장이 5~8개의 단어로 구성되었는지 확인하여 점수를 부여합니다.
- **이유**: 너무 짧거나 너무 긴 문장은 의미를 전달하기 어렵고, 문법적으로 완전하지 않을 가능성이 높습니다.
- **연구적 근거**: 문장의 적정 길이는 문맥적 자연스러움을 유지하는 데 중요합니다. 적정 길이를 벗어난 문장은 오류 확률이 높아진다는 연구 결과가 있습니다 [[4]](#4).

### 5. 문장 복잡도 검사 (Complexity Check)

- **처리 내용**: 어휘 수준(`vocabulary_level`)과 절의 개수(`sentence_complexity`)를 평가합니다.
- **이유**: 복잡한 문장 구조나 고급 어휘는 문장의 완성도를 높일 수 있습니다. 단순한 구문은 오류 가능성이 낮을 수 있지만, 지나치게 단순하면 문법적으로 부정확할 수 있습니다.
- **연구적 근거**: 문장의 복잡도는 문법 오류 감지에서 중요한 역할을 합니다. 지나치게 단순한 문장은 문법적 오류를 포함할 확률이 높다는 연구 결과가 있습니다 [[5]](#5).

### 6. 어휘 다양성 검사 (Lexical Diversity Check)

- **처리 내용**: 고유 단어 비율을 계산하여 어휘의 다양성을 평가합니다.
- **이유**: 단어의 반복 사용이 많으면 문장이 비문법적이거나 무의미할 가능성이 있습니다.
- **연구적 근거**: 어휘 다양성은 자연스러운 문장 구성을 위한 요소로, 문법 오류 감지 연구에서도 많이 사용됩니다 [[6]](#6).

### 7. 의미론적 코히런스 검사 (Semantic Coherence Check)

- **처리 내용**: Transformer 기반의 BERT 모델을 활용해 문장의 문법적 완성도를 평가합니다.
- **이유**: Transformer 모델은 문맥을 이해하는 데 탁월하며, 문법적으로 자연스러운 문장을 식별할 수 있습니다.
- **연구적 근거**: BERT와 같은 대규모 사전 학습 모델은 문맥적 자연스러움을 평가하는 데 유용하며, 문법 오류 감지 분야에서 높은 성능을 보여줍니다 [[7]](#7).

### 8. 강화된 의미 없는 단어 감지 및 반복 단어 패턴 검사 (Enhanced Meaningful Words Check)

- **처리 내용**: 의미 없는 단어(OOV)와 반복 패턴을 감지합니다. 사전에 없는 단어인지(`is_oov`) 확인하고, 단어가 비정상적으로 반복되는지, 특정 패턴을 이루는지 검사합니다.
- **이유**: 무의미한 단어가 포함된 문장이나 반복 패턴은 비문법적이거나 의미가 불분명할 가능성이 높습니다.
- **연구적 근거**: 무의미한 단어와 반복 패턴 감지는 문법 오류 감지에서 중요한 부분으로, 이들이 포함된 문장은 문맥적으로 자연스럽지 않은 경향이 있습니다 [[8]](#8).

---

## 참고문헌

1. <a name="1">SpaCy Documentation</a>. _NLP Library for Natural Language Processing_.
2. <a name="2">Bryant, C., Felice, M., Andersen, Ø. E., & Briscoe, T.</a> (2019). _Grammatical Error Correction: A Survey of the State of the Art_. Computational Linguistics.
3. <a name="3">Junczys-Dowmunt, M., Grundkiewicz, R., Dwojak, T., Heafield, K., Hoang, H., & Birch, A.</a> (2018). _Grammatical Error Correction with Neural Machine Translation_. ACL.
4. <a name="4">Kaneko, Y., & Komachi, M.</a> (2019). _BERT for Grammatical Error Correction in Non-native English_. ACL Workshop.
5. <a name="5">Toshniwal, S., Livescu, K., & Gimpel, K.</a> (2021). _Automatic Evaluation of Grammatical Error Correction Using Machine Translation Metrics_. ACL.
6. <a name="6">Dahlmeier, D., Ng, H. T., & Wu, S. M.</a> (2013). _A Benchmark Corpus and Evaluation Methodology for Grammatical Error Correction_. ACL Workshop.
7. <a name="7">Devlin, J., Chang, M. W., Lee, K., & Toutanova, K.</a> (2018). _BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding_. NAACL.
8. <a name="8">Mikhailov, N., Dobrev, G., Reznikova, Y., Ganchev, G., Sorokin, A., & Nakov, P.</a> (2020). _GECToR - Grammatical Error Correction: Tag, Not Rewrite_. ACL.
