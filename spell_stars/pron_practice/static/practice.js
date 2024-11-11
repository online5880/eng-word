let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let nativeAudioPreview = document.getElementById("native-audio-preview");
let countdownText = document.getElementById('countdown'); // 카운트다운을 표시할 요소

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;


// 페이지 로드 후 음성을 준비만 하고 자동으로 재생되지 않도록 설정
window.onload = function () {
    let nativeAudioPreview = document.getElementById("native-audio-preview");
    nativeAudioPreview.load();  // 음성을 로드만 시킴 (자동 재생 X)
};

// 오디오 재생을 위한 함수 (Play 버튼을 눌렀을 때)
function playNativeAudio() {
    let nativeAudioPreview = document.getElementById("native-audio-preview");
    nativeAudioPreview.play();  // 버튼 클릭 시 음성 재생
}


// 카운트다운 시작
function startCountdown() {
    countdownText.style.display = 'block'; // 카운트다운 영역을 보이게 설정
    let countdownNumbers = [3, 2, 1];
    let index = 0;

    function updateCountdown() {
        if (index < countdownNumbers.length) {
            countdownText.innerText = countdownNumbers[index];
            index++;
            setTimeout(updateCountdown, 1000); // 1초마다 숫자 변경
        } else {
            countdownText.style.display = 'none'; // 카운트다운 숨기기
            startRecording(); // 카운트다운이 끝나면 녹음 시작
        }
    }

    updateCountdown(); // 카운트다운 시작
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
        audioStream.getTracks().forEach(track => track.stop()); // 마이크 종료

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

