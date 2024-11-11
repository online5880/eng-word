let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let scoreDisplay = document.getElementById("score");
let score = 0;
let allWordsLearned = false; // 모든 단어가 학습되었는지 여부 확인
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

            // 발음 수준에 따라 다음 단어로 이동하거나 예문 학습 모드로 이동
            handleNextStep(score);
        })
        .catch(error => {
            console.error("Error processing recording: ", error);
            alert("서버 처리 중 오류가 발생했습니다.");
        });
}

// 피드백 표시
function displayFeedback(score, feedback) {
    scoreDisplay.textContent = score;

    if (score >= 80) {
        scoreDisplay.style.color = 'green';
    } else if (score >= 60) {
        scoreDisplay.style.color = 'yellow';
    } else {
        scoreDisplay.style.color = 'red';
    }
}

// 발음 평가 후 다음 단계로 이동
function handleNextStep(score) {
    // 발음 기준이 80 이상이면 다음 단어로 넘어가거나 예문 학습으로 이동
    if (score >= 80) {
        // 단어 세트를 모두 학습했으면 예문 학습 모드로 이동
        if (allWordsLearned) {
            window.location.href = '/vocab_mode/sent_pratice/';  // 예문 학습 모드로 리다이렉트
        } else {
            // 단어 세트를 모두 학습하지 않았다면 다음 단어로 이동
            window.location.href = '/vocab_mode/';  // 여기서 다음 단어로 이동하는 URL을 처리
        }
    } else {
        alert("발음이 기준에 미치지 못했습니다. 다시 시도해주세요.");
    }
}
