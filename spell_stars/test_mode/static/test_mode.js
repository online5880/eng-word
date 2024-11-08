let mediaRecorder;
let audioChunks = [];

function startRecording(questionId) {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                sendAudioToServer(audioBlob, questionId);
            };

            // 녹음이 완료되면 자동으로 서버에 전송
            document.getElementById(`status_${questionId}`).textContent = "녹음 중...";
        })
        .catch(error => {
            console.error("Error accessing microphone:", error);
            alert("마이크 접근에 문제가 발생했습니다. 권한을 확인해주세요.");
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        document.getElementById(`status_${questionId}`).textContent = "녹음 종료";
    }
}

function sendAudioToServer(audioBlob, questionId) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    fetch(`/test_mode/recognize/${questionId}/`, {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.transcript) {
                document.getElementById(`answer_${questionId}`).value = data.transcript;
            } else {
                document.getElementById(`status_${questionId}`).textContent = "인식 오류: 다시 시도해주세요.";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById(`status_${questionId}`).textContent = "서버 오류: 다시 시도해주세요.";
        });
}
