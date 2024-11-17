document.addEventListener('DOMContentLoaded', function() {
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
    }

    // 이전 버튼 클릭
    prevButton.addEventListener('click', () => {
        currentIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
        showCard(currentIndex);
    });

    // 다음 버튼 클릭
    nextButton.addEventListener('click', () => {
        currentIndex = currentIndex < cards.length - 1 ? currentIndex + 1 : 0;
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
                console.log(getCurrentWord())

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
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            micButton.classList.remove('recording');
            statusText.textContent = '녹음이 완료되었습니다.';
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
});
