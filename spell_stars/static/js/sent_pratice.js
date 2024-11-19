document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.word-card');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const cardIndex = document.getElementById('cardIndex');
    const audioPlayer = document.getElementById('audioPlayer');
    const micButton = document.getElementById('micButton');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    let currentIndex = 0;
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let passedWords = new Set();

    // beforeunload 이벤트 리스너 추가
    window.addEventListener('beforeunload', function(e) {
        fetch('/accounts/end-learning/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    });

    // 현재 단어 가져오기
    function getCurrentWord() {
        const currentCard = cards[currentIndex];
        return currentCard.querySelector('h3').textContent.trim();
    }

    // 카드 표시/숨김
    function showCard(index) {
        cards.forEach((card, i) => {
            card.style.display = i === index ? 'block' : 'none';
        });
        cardIndex.textContent = `${currentIndex + 1}/${cards.length}`;
        
        // 프로그레스 바 초기화
        const progressBar = document.getElementById("progressFill");
        const currentWord = getCurrentWord();
        
        if (passedWords.has(currentWord)) {
            progressBar.style.width = '100%';
            progressBar.style.backgroundColor = '#4CAF50';
            statusText.textContent = '이미 통과한 문장입니다!';
            statusText.style.color = '#4CAF50';
        } else {
            progressBar.style.width = '0%';
            progressBar.style.backgroundColor = '#f44336';
            statusText.textContent = '마이크를 클릭하여 시작하세요';
            statusText.style.color = '#666';
        }
        
        updateNavigationButtons();
    }

    function updateNavigationButtons() {
        prevButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === cards.length - 1 || !passedWords.has(getCurrentWord());
        
        [prevButton, nextButton].forEach(button => {
            if (button.disabled) {
                button.classList.add('disabled');
            } else {
                button.classList.remove('disabled');
            }
        });
    }

    prevButton.addEventListener('click', () => {
        currentIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
        stopRecording();
        showCard(currentIndex);
    });

    nextButton.addEventListener('click', () => {
        currentIndex = currentIndex < cards.length - 1 ? currentIndex + 1 : 0;
        stopRecording();
        showCard(currentIndex);
    });

    // 녹음 시작
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');
                formData.append('word', getCurrentWord());

                try {
                    const response = await fetch(uploadAudioUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        },
                        body: formData
                    });

                    if (response.ok) {
                        statusText.textContent = '녹음이 성공적으로 저장되었습니다.';
                        
                        // 응답 데이터를 JSON으로 변환
                        const data = await response.json();

                        // 결과 보여주기
                        displayResult(data.result.result)
                        
                    } else {
                        throw new Error('녹음 저장 실패');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    statusText.textContent = '녹음 저장 중 오류가 발생했습니다.';
                }
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add('recording');
            statusText.textContent = '녹음 중...';

            // 음성 레벨 표시
            const audioContext = new AudioContext();
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            function updateVoiceLevel() {
                if (isRecording) {
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                    const level = (average / 128) * 100;
                    voiceLevelFill.style.width = `${level}%`;
                    requestAnimationFrame(updateVoiceLevel);
                }
            }
            updateVoiceLevel();

        } catch (error) {
            console.error('Error:', error);
            statusText.textContent = '마이크 접근 오류';
        }
    }

    // 녹음 중지
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            statusText.textContent = '녹음이 완료되었습니다.';
            micButton.classList.remove('recording');
            voiceLevelFill.style.width = '0%';
        }
    }

    // 마이크 버튼 이벤트
    micButton.addEventListener('click', () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    function displayResult(result) {
        console.log("displayResult received result:", result);
    
        if (!result || typeof result.overall_score !== "number") {
            console.error("Error: result or overall_score is invalid", result);
            statusText.textContent = "결과를 불러오는 중 오류가 발생했습니다.";
            return;
        }
    
        const score = result.overall_score;
        const currentWord = getCurrentWord();
        
        // 점수가 80점 이상이면 통과 처리
        if (score >= 80) {
            passedWords.add(currentWord);
            statusText.textContent = `발음 점수: ${score.toFixed(2)}점 - 통과!`;
            statusText.style.color = '#4CAF50';  // 초록색으로 표시
            
            // 모든 단어가 통과되었는지 확인
            if (checkAllWordsPassed()) {
                sentenceModeButton.style.display = 'flex';
            }
        } else {
            statusText.textContent = `발음 점수: ${score.toFixed(2)}점 - 다시 시도하세요`;
            statusText.style.color = '#f44336';  // 빨간색으로 표시
        }
    
        // 진행률 바 업데이트
        const progressBar = document.getElementById("progressFill");
        progressBar.style.width = `${score}%`;
        progressBar.style.backgroundColor = score >= 80 ? '#4CAF50' : '#f44336';
        
        updateNavigationButtons();  // 버튼 상태 업데이트
    }

    // 모든 단어가 통과되었는지 확인하는 함수
    function checkAllWordsPassed() {
        const allWords = Array.from(cards).map(card => 
            card.querySelector('h3').textContent.trim()
        );
        return allWords.every(word => passedWords.has(word));
    }

    // 초기 카드 표시
    showCard(currentIndex);
});
