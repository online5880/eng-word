# DTW

# 포인트주파수

# vost

```
1. 발음 정확도 평가에 적합한 이유

    낮은 WER (Word Error Rate): vosk-model-en-us-0.22의 Word Error Rate(WER)은 5.69로, 이는 음성 인식에서 매우 낮은 편에 속합니다. WER이 낮을수록 인식 정확도가 높기 때문에, 발음 평가 시에도 정확한 텍스트 변환을 기대할 수 있습니다.
    정밀한 음성 인식: vosk-model-en-us-0.22는 다양한 미국 영어 발음을 정확하게 인식하도록 훈련되었습니다. 발음 평가에서는 학습자가 발음한 단어를 정확히 인식하는 것이 중요하므로, 이 모델의 높은 인식 정확도는 발음 평가에 큰 도움이 됩니다.
    다양한 상황에서의 적용 가능성: 이 모델은 다양한 데이터셋으로 훈련되어 일상적인 미국 영어 발음 인식에 최적화되어 있습니다. 이는 학습자의 발음이 원어민 발음에 어느 정도 근접한지를 평가하는 데 유용합니다.

2. 최근 사용 경향

    오프라인 음성 인식에서 인기: vosk-model-en-us-0.22는 오프라인 환경에서도 정확한 인식을 제공하기 때문에, 개인 데이터 보호가 중요한 환경이나 네트워크가 없는 환경에서 많이 사용되고 있습니다.
    발음 평가 및 언어 학습 응용 분야에서 사용: Vosk 모델은 최근 언어 학습 앱이나 발음 평가 시스템에서 많이 활용되고 있습니다. 오프라인으로도 사용할 수 있기 때문에, 온라인 API 사용에 제한이 있거나 비용이 걱정되는 경우 대안으로 많이 선택됩니다.
    학습 자료 분석 및 교육용 앱에서의 활용: 이 모델은 비교적 최신 데이터셋을 기반으로 훈련되었기 때문에, 교육 분야에서도 정확하고 신뢰성 있는 성능을 제공합니다.

3. 발음 평가에 좋은 이유 요약

    높은 정확도: 발음 평가에서는 학습자의 발음을 원어민 발음과 얼마나 유사한지를 측정해야 하는데, 이 모델은 높은 WER 성능을 제공하므로 학습자가 발음한 단어를 정확하게 인식하는 데 유리합니다.
    오프라인 작동: Vosk의 en-us-0.22 모델은 오프라인에서도 정확히 작동하여 비용이나 네트워크 문제 없이도 발음 평가가 가능합니다.
    다양한 발음에 대한 적응성: 학습자가 다양한 억양이나 발음으로 영어 단어를 발음할 때도 일정 수준의 정확도를 기대할 수 있습니다.
    따라서, vosk-model-en-us-0.22는 초등 수준 단어 발음 평가와 같은 용도에 있어서, 높은 정확도를 제공할 수 있는 좋은 선택입니다.

```

# 종합점수

## 발음 평가를 위한 가중치 설정에 대한 연구 및 추천

발음 평가 연구에서 **Phoneme-Level Accuracy(음소 정확도)**와 **Formant Analysis(포먼트 분석)**는 발음의 **정확성**과 **명료성**을 평가하는 중요한 지표입니다. 최신 연구들은 Phoneme-Level Accuracy에 더 높은 가중치를 부여하는 경향이 있습니다.

---

## 1. 각 지표의 역할

- **Phoneme-Level Accuracy**: 발음의 음소 단위 정확성을 평가하여 단어 발음이 예상 단어와 얼마나 유사한지를 판단합니다. 발음의 정확도를 평가하는 데 핵심적인 요소입니다.
- **Formant Analysis**: 발음의 음질과 모음 발음의 주파수 영역을 평가하여 발음의 명료성을 판단합니다. 발음의 자연스러움과 음질을 측정하는 데 유용합니다.

---

## 2. 관련 연구 및 권장 가중치

### (1) Automatic Pronunciation Evaluation 연구

- **논문**: "Automatic Pronunciation Evaluation of Second Language Learners Using Phoneme-level Features"
- **내용**: Phoneme-Level Accuracy가 발음 평가에서 중요한 요소로, 특히 학습자의 발음 정확도를 높게 평가하는 지표임을 강조.
- **결론**: Phoneme-Level Accuracy에 더 높은 가중치를 두는 것이 발음 평가에 효과적임을 확인.

### (2) Formant-based Pronunciation Scoring 연구

- **논문**: "Improving Pronunciation Assessment using Formant Features"
- **내용**: Formant Analysis가 발음의 음질과 명료성을 평가하는 데 유용하나, 정확도 측면에서는 Phoneme-Level Accuracy가 더 중요한 역할을 함.
- **결론**: Phoneme-Level Accuracy에 더 높은 가중치를 부여하고, Formant Score는 보조 지표로 사용을 권장.

### (3) 종합 발음 평가 시스템 연구

- **논문**: "A Comprehensive Framework for Automatic Pronunciation Evaluation"
- **내용**: 발음 평가에서 Phoneme-Level Accuracy와 Formant Score의 가중치를 각각 0.6과 0.4로 설정하는 것을 추천. 두 지표가 상호 보완적인 역할을 함.
- **결론**: 발음 정확성을 평가하기 위해 Phoneme-Level Accuracy에 더 높은 가중치를 설정하는 것이 적절.

---

## 3. 최종 가중치 설정 (추천)

- **Phoneme-Level Accuracy**: 0.6 (발음의 정확성을 직접적으로 평가)
- **Formant Score**: 0.4 (발음의 음질과 명료성을 평가)

### 가중치 설정 이유

Phoneme-Level Accuracy는 발음의 정확성을 판단하는 데 가장 중요한 요소이며, Formant Score는 보조적으로 발음의 음질을 평가하는 요소로 작용합니다. 연구에 따르면 Phoneme-Level Accuracy에 더 높은 가중치를 두는 것이 발음 평가의 신뢰성을 높이는 데 효과적입니다.

---
