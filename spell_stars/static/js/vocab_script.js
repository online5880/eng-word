document.addEventListener('DOMContentLoaded', function() {
    const playButton = document.getElementById('playAudioButton');
    const audioPlayer = document.getElementById('audioPlayer');
    const micButton = document.getElementById('micButton');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    const progressFill = document.getElementById('progressFill');
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // 오디오 재생 버튼 이벤트
    if (playButton && audioPlayer) {
        playButton.addEventListener('click', function() {
            if (audioPlayer.src) {
                console.log('오디오 재생 시도:', audioPlayer.src); // 디버깅용
                audioPlayer.load(); // 오디오 다시 로드
                audioPlayer.play()
                    .then(() => {
                        console.log('오디오 재생 성공');
                    })
                    .catch(function(error) {
                        console.error('오디오 재생 오류:', error);
                    });
            } else {
                console.error('오디오 소스가 없습니다');
            }
        });
    }

    // 마이크 버튼 이벤트
    if (micButton) {
        micButton.addEventListener('click', async function() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    startRecording(stream);
                } catch (err) {
                    console.error('마이크 접근 오류:', err);
                    statusText.textContent = '마이크 접근이 거부되었습니다.';
                }
            } else {
                stopRecording();
            }
        });
    }

    function startRecording(stream) {
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;

        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const word = document.querySelector('#playAudioButton').getAttribute('data-word');
            
            const formData = new FormData();
            formData.append('audio', audioBlob, `${word}.wav`);
            formData.append('word', word);

            try {
                const response = await fetch(uploadAudioUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    statusText.textContent = '녹음이 성공적으로 저장되었습니다.';
                    // 오디오 플레이어 소스 업데이트
                    if (audioPlayer) {
                        audioPlayer.src = '/' + data.file_path;
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
                const level = (average / 255) * 100;
                voiceLevelFill.style.height = `${level}%`;
                requestAnimationFrame(updateVoiceLevel);
            }
        }
        updateVoiceLevel();
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            statusText.textContent = '녹음이 완료되었습니다.';
            micButton.classList.remove('recording');
            voiceLevelFill.style.height = '0%';
        }
    }
});