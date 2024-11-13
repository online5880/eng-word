let currentWordIndex = 0;
let recognition;
let isRecording = false;
let audioContext;
let analyser;
let microphone;

const voiceLevelFill = document.querySelector('.voice-level-fill');
const statusText = document.querySelector('.status-text');
const micStatus = document.querySelector('.mic-status');

// 음성 레벨 분석 설정
async function setupAudioContext() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        analyser.fftSize = 256;
        updateVoiceLevel();
    } catch (error) {
        console.error('마이크 접근 오류:', error);
        statusText.textContent = '마이크 접근이 거부되었습니다.';
    }
}

// 음성 레벨 업데이트
function updateVoiceLevel() {
    if (!isRecording) return;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    const level = Math.min(100, (average / 128) * 100);
    
    voiceLevelFill.style.width = `${level}%`;
    requestAnimationFrame(updateVoiceLevel);
}

// 음성 인식 초기화
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = function() {
        statusText.textContent = '말씀해 주세요...';
    };

    recognition.onresult = function(event) {
        const result = event.results[0][0].transcript.toLowerCase();
        const currentWord = words[currentWordIndex].text.toLowerCase();
        
        const similarity = calculateSimilarity(result, currentWord);
        document.getElementById('progressFill').style.width = `${similarity * 100}%`;
        
        if (similarity > 0.8) {
            statusText.textContent = '정확합니다!';
            setTimeout(nextWord, 1000);
        } else {
            statusText.textContent = '다시 시도해주세요.';
        }
    };

    recognition.onend = function() {
        const micButton = document.getElementById('micButton');
        micButton.classList.remove('recording');
        micStatus.classList.remove('recording');
        voiceLevelFill.style.width = '0%';
        isRecording = false;
        statusText.textContent = '마이크를 클릭하여 시작하세요';
    };

    recognition.onerror = function(event) {
        statusText.textContent = `오류 발생: ${event.error}`;
        console.error('Speech recognition error:', event.error);
    };
}

// 기존의 calculateSimilarity 함수와 nextWord 함수는 유지

// 녹음 버튼 이벤트 수정
document.getElementById('micButton').addEventListener('click', async function() {
    if (!audioContext) {
        await setupAudioContext();
    }

    if (!isRecording) {
        recognition.start();
        this.classList.add('recording');
        updateVoiceLevel();
    } else {
        recognition.stop();
        this.classList.remove('recording');
        voiceLevelFill.style.width = '0%';
    }
    isRecording = !isRecording;
});

function playAudio() {
    const audioPlayer = document.getElementById("audioPlayer");
    if (audioPlayer) {
        audioPlayer.play();
    }
}