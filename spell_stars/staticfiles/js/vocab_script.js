document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.word-card');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const cardIndex = document.getElementById('cardIndex');
    const audioPlayer = document.getElementById('audioPlayer');
    const micButton = document.getElementById('micButton');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    const sentenceModeButton = document.getElementById('sentenceModeButton');
    let currentIndex = 0;
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let passedWords = new Set();  // 통과한 단어들을 저장할 Set

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
    
        const progressBar = document.getElementById("progressFill");
        const currentWord = getCurrentWord();
        const wave_figContainer = document.getElementById("wave_fig_container");
        const formant_figContainer = document.getElementById("formant_fig_container");
    
        if (passedWords.has(currentWord)) {
            // 이미 통과한 단어인 경우
            progressBar.style.width = '100%';
            progressBar.style.backgroundColor = '#4CAF50';
            statusText.textContent = '이미 통과한 단어입니다!';
            statusText.style.color = '#4CAF50';
    
            // 그래프 표시
            if (wordGraphs.has(currentWord)) {
                wave_figContainer.innerHTML = wordGraphs.get(currentWord);
                formant_figContainer.innerHTML = wordGraphs.get(currentWord);
            } else {
                wave_figContainer.innerHTML = ''; // 그래프가 없으면 초기화
                formant_figContainer.innerHTML = ''; // 그래프가 없으면 초기화
            }
        } else {
            // 아직 통과하지 못한 단어인 경우
            progressBar.style.width = '0%';
            progressBar.style.backgroundColor = '#f44336';
            statusText.textContent = '마이크를 클릭하여 시작하세요';
            statusText.style.color = '#666';
    
            // 그래프 숨기기
            wave_figContainer.innerHTML = '';
            formant_figContainer.innerHTML = '';
        }
    
        updateNavigationButtons();
    }
    

    // 버튼 상태 업데이트 함수 추가
    function updateNavigationButtons() {
        // 현재 단어가 통과했거나, 이전 단어로 가는 경우에만 버튼 활성화
        prevButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === cards.length - 1 || !passedWords.has(getCurrentWord());
        
        // 버튼 스타일 업데이트
        [prevButton, nextButton].forEach(button => {
            if (button.disabled) {
                button.classList.add('disabled');
            } else {
                button.classList.remove('disabled');
            }
        });
    }

    // 이전 버튼 클릭
    prevButton.addEventListener('click', () => {
        currentIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
        stopRecording();
        showCard(currentIndex);
    });

    // 다음 버튼 클릭
    nextButton.addEventListener('click', () => {
        currentIndex = currentIndex < cards.length - 1 ? currentIndex + 1 : 0;
        stopRecording();
        showCard(currentIndex);
    });

    // 녹음 시작
    async function startRecording() {
        try {
            console.log('Starting recording...');
    
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('Stream received:', stream);
    
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
    
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
    
            mediaRecorder.onstop = async () => {
                console.log('Recording stopped. Processing audio...');

                // 데이터 확인
                console.log('audioChunks:', audioChunks);
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                console.log('audioBlob:', audioBlob);

                const currentWord = getCurrentWord();
                console.log('currentWord:', currentWord);

                const formData = new FormData();
                formData.append('audio', audioBlob, `${currentWord}.wav`);
                formData.append('word', currentWord);

                console.log("==")

                // FormData 확인
                for (let pair of formData.entries()) {
                    console.log(`${pair[0]}: ${pair[1]}`);
                }
                console.log("==")
                
            
                try {
                    const response = await fetch(uploadAudioUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        },
                        body: formData
                    });
                    
    
                    console.log('Response status:', response.status);
                    if (response.ok) {
                        const data = await response.json();
                        console.log('Upload success:', data);
                        displayResult(data.result);
                    } else {
                        const errorText = await response.text();
                        console.error('Upload failed:', errorText);
                        statusText.textContent = '녹음 저장 중 오류가 발생했습니다.';
                    }
                } catch (error) {
                    console.error('Fetch error:', error);
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
            console.error('Error in startRecording:', error);
            statusText.textContent = '마이크 접근 오류';
        }
    }

    // 녹음 중지
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            document.querySelector('.spinner-container').style.display = 'block'; // 스피너 표시
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

    // 원어민 발음 듣기
    document.querySelectorAll('.playAudioButton').forEach(button => {
        button.addEventListener('click', function() {
            const audioUrl = this.getAttribute('data-audio');
            audioPlayer.src = audioUrl;
            audioPlayer.play();
        });
    });

    // 초기 상태 설정
    showCard(currentIndex);

    
    const wordGraphs = new Map(); // 단어별 그래프 저장소
    function displayResult(result) {
        document.querySelector('.spinner-container').style.display = 'none'; // 스피너 숨기기
        
        if (!result || typeof result.overall_score !== "number") {
            console.error("Error: result or overall_score is invalid", result);
            statusText.textContent = "결과를 불러오는 중 오류가 발생했습니다.";
            return;
        }
    
        const score = result.overall_score;
        const currentWord = getCurrentWord();
    
        // 점수가 70점 이상이면 통과 처리
        if (score >= 70) {
            passedWords.add(currentWord);
            statusText.textContent = `발음 점수: ${score.toFixed(2)}점 - 통과!`;
            statusText.style.color = '#4CAF50'; // 초록색으로 표시
    
            // 모든 단어가 통과되었는지 확인
            if (checkAllWordsPassed()) {
                sentenceModeButton.style.display = 'flex';
            }
        } else {
            statusText.textContent = `발음 점수: ${score.toFixed(2)}점 - 다시 시도하세요`;
            statusText.style.color = '#f44336'; // 빨간색으로 표시
        }
    
        // 진행률 바 업데이트
        const progressBar = document.getElementById("progressFill");
        progressBar.style.width = `${score}%`;
        progressBar.style.backgroundColor = score >= 70 ? '#4CAF50' : '#f44336';
    
        // HTML 그래프 삽입
        const wave_figContainer = document.getElementById("wave_fig_container");
        const formant_figContainer = document.getElementById("formant_fig_container");

        if (result && result.wave_html_fig && result.formant_html_fig) {
            const parser = new DOMParser();

            // waveform
            const wave_parsedDoc = parser.parseFromString(result.wave_html_fig, "text/html");

            // 그래프 저장
            wordGraphs.set(currentWord, wave_parsedDoc.body.innerHTML);

            // DOM 요소 삽입
            wave_figContainer.innerHTML = wave_parsedDoc.body.innerHTML;

            // 스크립트 태그 동적으로 실행
            const waveform_scripts = wave_parsedDoc.querySelectorAll("script");
            waveform_scripts.forEach(script => {
                const newScript = document.createElement("script");
                newScript.textContent = script.textContent;
                document.body.appendChild(newScript);
            });

            // formant
            const formant_parsedDoc = parser.parseFromString(result.formant_html_fig, "text/html");

            // 그래프 저장
            wordGraphs.set(currentWord, formant_parsedDoc.body.innerHTML);

            // DOM 요소 삽입
            formant_figContainer.innerHTML = formant_parsedDoc.body.innerHTML;

            // 스크립트 태그 동적으로 실행
            const formant_scripts = formant_parsedDoc.querySelectorAll("script");
            formant_scripts.forEach(script => {
                const newScript = document.createElement("script");
                newScript.textContent = script.textContent;
                document.body.appendChild(newScript);
            });
        } else {
            console.error("HTML figure not found in response.");
        }
    
        updateNavigationButtons(); // 버튼 상태 업데이트
    }

    function checkAllWordsPassed() {
        const allWords = Array.from(cards).map(card => 
            card.querySelector('h3').textContent.trim()
        );
    
        console.log('All words:', allWords);
        console.log('Passed words:', Array.from(passedWords));
    
        return allWords.every(word => passedWords.has(word));
    }
    
    // 예문 학습 버튼 클릭 이벤트
    sentenceModeButton.addEventListener('click', () => {
        // 세션 종료 요청 보내기
        fetch('/accounts/end-learning/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        }).then(() => {
            // 예문 학습 페이지로 이동 ('/sent/'로 수정)
            window.location.href = '/sent/';
        });
    });
});
