let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let nativeAudioPreview = document.getElementById("native-audio-preview");

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// 원어민 음성 재생
function loadNativeAudio() {
    let nativeAudioUrl = '/media/audio/native/eraser_a.wav';
    nativeAudioPreview.src = nativeAudioUrl;
    nativeAudioPreview.style.display = 'block';
    nativeAudioPreview.load();
    nativeAudioPreview.play();
}

// 녹음 시작
function startRecording() {
    if (navigator.mediaDevices) {
        audioData = [];

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                recorder = new MediaRecorder(stream);

                recorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioData.push(event.data);
                    }
                };

                recorder.onstop = () => {
                    if (audioData.length > 0) {
                        processRecording();
                    } else {
                        alert("녹음 데이터가 없습니다. 다시 시도해주세요.");
                    }
                };

                // 녹음 시작 지연 추가
                setTimeout(() => {
                    recorder.start(); // 녹음 시작
                    document.getElementById("startBtn").disabled = true;
                    document.getElementById("stopBtn").disabled = false;
                }, 300); // 300ms 지연 추가

            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("녹음 시작에 실패했습니다. 마이크 권한을 확인해주세요.");
            });
    }
}

// 녹음 종료
function stopRecording() {
    if (recorder && recorder.state === 'recording') {
        recorder.stop();
        audioStream.getTracks().forEach(track => track.stop());

        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
}

// 녹음 처리
function processRecording() {
    const audioBlob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    formData.append('target_word', currentWord);

    fetch('/pron_practice/evaluate_pronunciation/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            const score = data.score;
            const feedback = data.feedback;
            displayFeedback(score, feedback);

            const audioUrl = URL.createObjectURL(audioBlob);
            audioPreview.src = audioUrl;
            audioPreview.style.display = 'block';
        })
        .catch(error => {
            console.error("Error processing recording: ", error);
            alert("서버 처리 중 오류가 발생했습니다.");
        });
}

// 피드백 표시
function displayFeedback(score, feedback) {
    document.getElementById("score").textContent = score;
    document.getElementById("score-bar").style.width = score + "%";

    const feedbackSection = document.getElementById("feedback-section");
    const feedbackDisplay = document.getElementById("feedback");
    feedbackDisplay.textContent = feedback;
    feedbackSection.style.display = 'block';

    const progressBar = document.getElementById('score-bar');
    if (score >= 80) {
        progressBar.className = 'green';
    } else if (score >= 60) {
        progressBar.className = 'yellow';
    } else {
        progressBar.className = 'red';
    }
}

// 다음 단어로 이동
function nextWord() {
    window.location.href = '/pron_practice/next_word/';
}

// 연습 종료
function exitPractice() {
    window.location.href = '/';
}

// 페이지 로드 시 원어민 음성 로드
window.onload = function () {
    loadNativeAudio();
}
