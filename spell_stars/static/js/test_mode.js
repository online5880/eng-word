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
                // 녹음이 끝난 후 Blob을 생성하고 URL을 할당
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioUrl = URL.createObjectURL(audioBlob);

                // 오디오 미리보기
                audioPreview.src = audioUrl;

                // 서버로 오디오 전송
                sendAudioToServer(audioBlob);
            };

            // 버튼 상태 변경
            document.getElementById("stop-recording").disabled = false;
            document.getElementById("start-recording").disabled = true;
        })
        .catch(error => {
            console.error('Error accessing media devices.', error);
            document.getElementById("error-message").textContent = "음성 녹음 장치를 사용할 수 없습니다.";
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
            resultDiv.className = "green";  // 결과 색상 변경
        } else {
            resultDiv.textContent = "음성 인식에 실패했습니다.";
            resultDiv.className = "red";  // 결과 색상 변경
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const resultDiv = document.getElementById("audio-result");
        resultDiv.textContent = "서버와의 통신 중 오류가 발생했습니다.";
        resultDiv.className = "red";
    });
}
