document.addEventListener('DOMContentLoaded', function () {
    const micButton = document.getElementById('micButton');
    const audioPlayer = document.getElementById('audioPlayer');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const nextQuestionBtn = document.getElementById("nextQuestionBtn");  // 다음 문제 버튼
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let targetedWord = '';

    // 초기 상태로 버튼을 비활성화
    if (nextQuestionBtn) {
        nextQuestionBtn.disabled = true; // 처음에는 비활성화
    }

    // 마이크 버튼 이벤트
    if (micButton) {
        micButton.addEventListener('click', async function () {
            if (!isRecording) {
                try {
                    console.log('마이크 접근 시도...');
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    console.log('마이크 접근 성공');
                    startRecording(stream);
                } catch (err) {
                    console.error('마이크 접근 오류:', err);
                    statusText.textContent = '마이크 접근이 거부되었습니다.';
                }
            } else {
                console.log('녹음 중... 녹음 종료');
                stopRecording();
            }
        });
    }

    // 녹음 시작
    function startRecording(stream) {
        console.log('녹음 시작');
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;

        mediaRecorder.addEventListener('dataavailable', event => {
            console.log('오디오 데이터 수집:', event.data);
            audioChunks.push(event.data);
        });

        // 녹음 종료 후 서버에서 점수 받기
        mediaRecorder.addEventListener('stop', async () => {
            console.log('녹음 종료');
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

            const formData = new FormData();
            const targetedWord = document.getElementById('targeted-word').textContent; 
            formData.append('audio', audioBlob, `${targetedWord}.wav`);
            formData.append('word', targetedWord);

            const uploadAudioUrl = '/test/submit_audio/';
            try {
                console.log('오디오 업로드 시도');
                const response = await fetch(uploadAudioUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();
                console.log('서버 응답:', data);
                if (data.file_path) {
                    statusText.textContent = '녹음이 성공적으로 저장되었습니다.';
                    if (audioPlayer) {
                        audioPlayer.src = '/' + data.file_path;
                    }

                    // 서버에서 점수 받기
                    if (data.score_message !== undefined) {
                        console.log('서버에서 받은 점수:', data.score_message);
                        const scoreDisplay = document.getElementById("scoreDisplay");
                        if (scoreDisplay) {
                            scoreDisplay.textContent = data.score_message;
                        }

                        // **버튼 활성화 로직 수정**
                        // 데이터에서 `score_message`가 존재하는지 확인 후 활성화
                        if (scoreDisplay) {
                            nextQuestionBtn.disabled = false;  // 문제를 풀었으면 버튼 활성화
                        } else {
                            nextQuestionBtn.disabled = true;  // 점수가 없으면 버튼 비활성화
                        }
                    }
                } else {
                    statusText.textContent = '녹음 저장에 실패했습니다.';
                }
            } catch (error) {
                console.error('녹음 저장 오류:', error);
                statusText.textContent = '녹음 저장 중 오류가 발생했습니다.';
            }
        });

        mediaRecorder.start();
        statusText.textContent = '녹음 중...';
        micButton.classList.add('recording');

        // 음성 레벨 표시
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function updateVoiceLevel() {
            if (isRecording) {
                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                const level = (average / 128) * 100;  // 음성 레벨 계산 수정
                voiceLevelFill.style.width = `${level}%`;  // 여기도 높이로 변경
                requestAnimationFrame(updateVoiceLevel);
            }
        }
        updateVoiceLevel();
    }

    // 녹음 종료
    function stopRecording() {
        console.log('녹음 종료 함수 실행');
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            statusText.textContent = '녹음이 완료되었습니다.';
            micButton.classList.remove('recording');
            voiceLevelFill.style.width = '0%';
        }
    }

    // 다음 문제 요청 시 단어 갱신
    function nextQuestion() {
        console.log('다음 단어 요청');
        fetch('/test/next_question/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('다음 단어 응답:', data);
            if (data.success) {
                const problemNumberElement = document.getElementById('problem-number');
                if (problemNumberElement) {
                    // 문제 번호 업데이트
                    problemNumberElement.textContent = `문제 번호: ${data.problem_solved}`;
                    console.log('문제 번호 갱신:', problemNumberElement.textContent);
                } else {
                    console.error('#problem-number 요소를 찾을 수 없습니다.');
                }

                if (nextQuestionBtn) {
                    nextQuestionBtn.disabled = true; // 처음에는 비활성화
                }
                
                // 단어 갱신
                document.getElementById('targeted-word').textContent = data.word;
    
                // 예문 갱신
                document.getElementById('sentence').textContent = data.sentence;
                document.getElementById('sentence-meaning').textContent = data.sentence_meaning;
    
                // 점수 초기화
                document.getElementById("scoreDisplay").textContent = '';

                // 상태 메시지 초기화
                statusText.textContent = '마이크를 클릭하여 시작하세요'; // 메시지 제거
    
                // 버튼 텍스트 및 이벤트 갱신
                if (data.is_last_question) {
                    nextQuestionBtn.textContent = '나가기';
                    nextQuestionBtn.removeEventListener('click', nextQuestion);
                    nextQuestionBtn.addEventListener('click', exitTest);
                } else {
                    nextQuestionBtn.textContent = '다음 문제';
                    nextQuestionBtn.removeEventListener('click', exitTest);
                    nextQuestionBtn.addEventListener('click', nextQuestion);
                }

            } else {
                console.log('새 단어를 가져오지 못했습니다.');
                alert('모든 문제를 완료했습니다. 새로 시작하려면 학습을 종료하고 다시 시작하세요.');
            }
        })
        .catch(error => {
            console.error('AJAX 요청 오류:', error);
        });
    }    

    // 나가기 버튼 클릭 시 학습 종료
    function exitTest() {
        window.location.href = 'results';  // 결과 페이지로 리디렉션
    }

    // 이벤트 리스너 추가
    if (nextQuestionBtn) {
        nextQuestionBtn.addEventListener('click', nextQuestion);
    }
});
