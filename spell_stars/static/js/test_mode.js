let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;
let audioPreview = document.getElementById("audio-preview");

// 녹음 시작 버튼 클릭
document.getElementById("start-recording").onclick = function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = function() {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioUrl = URL.createObjectURL(audioBlob);
                audioPreview.src = audioUrl;

                // 녹음이 끝난 후 서버로 오디오 전송
                sendAudioToServer(audioBlob);
            };

            document.getElementById("stop-recording").disabled = false;
            document.getElementById("start-recording").disabled = true;
        });
};

// 녹음 중지 버튼 클릭
document.getElementById("stop-recording").onclick = function() {
    mediaRecorder.stop();
    document.getElementById("start-recording").disabled = false;
    document.getElementById("stop-recording").disabled = true;
};

// 음성 파일을 서버로 전송
function sendAudioToServer(audioBlob) {
    let formData = new FormData();
    formData.append("audio", audioBlob, "audio.wav");

    fetch("{% url 'recognize_audio' 1 %}", {  // '1'은 예시 question_id
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById("audio-result");

        if (data.transcript) {
            resultDiv.textContent = "음성 인식 결과: " + data.transcript;
            resultDiv.style.color = "green";
        } else {
            resultDiv.textContent = "음성 인식에 실패했습니다.";
            resultDiv.style.color = "red";
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
