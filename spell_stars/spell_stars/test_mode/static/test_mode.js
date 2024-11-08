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

            setTimeout(() => {
                mediaRecorder.stop();
            }, 3000);  // 3초간 녹음
        });
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
        document.getElementById(`answer_${questionId}`).value = data.transcript;
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
