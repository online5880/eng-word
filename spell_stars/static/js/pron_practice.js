document.addEventListener('DOMContentLoaded', function () {
    const playButton = document.getElementById('playAudioButton');
    const audioPlayer = document.getElementById('audioPlayer');
    const micButton = document.getElementById('micButton');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // beforeunload 이벤트 리스너 추가
    window.addEventListener('beforeunload', function(e) {
        fetch('/accounts/end-learning/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    });

    // 페이지 로드 후 오디오 준비 (자동 재생 X)
    window.onload = function () {
        if (audioPlayer) {
            console.log('오디오 로드:', audioPlayer.src);
            audioPlayer.load();
        }
    };

    // 오디오 재생 버튼 이벤트
    if (playButton && audioPlayer) {
        playButton.addEventListener('click', function () {
            if (audioPlayer.src) {
                console.log('오디오 재생 시도:', audioPlayer.src);
                audioPlayer.load();
                audioPlayer.play()
                    .then(() => {
                        console.log('오디오 재생 성공');
                    })
                    .catch(function (error) {
                        console.error('오디오 재생 오류:', error);
                    });
            } else {
                console.error('오디오 소스가 없습니다');
            }
        });
    }

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

                const targetedWord = document.getElementById('current-word').textContent; 
                const formData = new FormData();
                formData.append('audio', audioBlob, `${targetedWord}.wav`);
                formData.append('word', targetedWord);

                // FormData 확인
                for (let pair of formData.entries()) {
                    console.log(`${pair[0]}: ${pair[1]}`);
                }
    
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
                        displayResult(data.score);
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

    // 피드백 표시
    function displayResult(score) {
        console.log(`점수: ${score}`);
        document.getElementById("score").textContent = score;  // 점수 업데이트
        document.getElementById("score-bar").style.width = score + "%";  // 점수에 맞는 프로그레스 바 업데이트

        const progressBar = document.getElementById('score-bar');
        if (score >= 80) {
            progressBar.className = 'green';  // 80점 이상은 녹색
        } else if (score >= 60) {
            progressBar.className = 'yellow';  // 60점 이상은 노란색
        } else {
            progressBar.className = 'red';  // 그 외 점수는 빨간색
        }
    }

    // 다음 단어로 이동
    function nextWord() {
        console.log('다음 단어 요청');
        fetch('/practice/next_word/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('다음 단어 응답:', data);
            if (data.success) {
                // 단어 갱신
                document.getElementById('current-word').textContent = data.nextWord;

                // 뜻 갱신
                document.getElementById('current-meaning').textContent = data.nextMeanings;

                // 오디오 파일 경로 갱신
                const audioPreview = document.getElementById('native-audio-preview');
                const source = audioPreview.querySelector('source');
                source.src = `/media/${data.nextFilePath}`;
                audioPreview.load();

                // 점수 초기화 및 갱신
                document.getElementById("score").textContent = '0';
                document.getElementById("score-bar").style.width = '0%';
                document.getElementById("feedback").textContent = '';
                document.getElementById("feedback-section").style.display = 'none';

                // 상태 메시지 초기화
                statusText.textContent = '마이크를 클릭하여 시작하세요'; // 메시지 제거
            } else {
                console.log('새 단어를 가져오지 못했습니다.');
            }
        })
        .catch(error => {
            console.error('AJAX 요청 오류:', error);
        });
    }


    // 연습 종료
    function exitPractice() {
        console.log('연습 종료');
        window.location.href = '/';
    }

    // 이벤트 리스너 추가
    const nextWordButton = document.getElementById("nextWordButton");
    const exitPracticeButton = document.getElementById("exitPracticeButton");

    if (nextWordButton) {
        nextWordButton.addEventListener('click', nextWord);
    }

    if (exitPracticeButton) {
        exitPracticeButton.addEventListener('click', exitPractice);
    }
});
