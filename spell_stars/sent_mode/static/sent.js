let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let feedbackDisplay = document.getElementById("feedback");
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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

                recorder.start();
                document.getElementById("startBtn").disabled = true;
                document.getElementById("stopBtn").disabled = false;
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
    feedbackDisplay.textContent = feedback;

    if (score >= 80) {
        feedbackDisplay.style.color = 'green';
    } else if (score >= 60) {
        feedbackDisplay.style.color = 'yellow';
    } else {
        feedbackDisplay.style.color = 'red';
    }
}

// 정답 제출
function submitAnswer() {
    // 예문 학습에서 정답 제출 및 피드백 표시 로직을 처리합니다.
    alert("정답 제출 완료! 예문 학습이 끝났습니다.");
    // 예시: window.location.href = '/next_word/';
}
