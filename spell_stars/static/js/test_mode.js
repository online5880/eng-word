let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;
let audioPreview = document.getElementById("audio-preview");
let audioStream;  // 마이크 스트림을 저장할 변수

// 녹음 시작 버튼 클릭
document.getElementById("start-recording").onclick = function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioStream = stream;  // 마이크 스트림 저장
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

                // 서버로 오디오 전송 (수정된 방식)
                saveAudioToServer(audioBlob);
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
    
    // 녹음이 끝난 후 마이크 스트림을 종료
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());  // 마이크 종료
    }

    // 버튼 상태 변경
    document.getElementById("start-recording").disabled = false;
    document.getElementById("stop-recording").disabled = true;
};

// 음성 파일을 서버에 저장 (수정된 부분)
function saveAudioToServer(audioBlob) {
    let formData = new FormData();
    formData.append("audio_file", audioBlob, "audio.wav");

    // JavaScript에서 questionId를 사용해 URL을 동적으로 만듭니다.
    fetch(`/recognize_audio/${questionId}/`, {  // questionId를 URL에 동적으로 삽입
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById("audio-result");

        if (data.message) {  // 서버에서의 응답
            resultDiv.textContent = "파일이 성공적으로 저장되었습니다.";
            resultDiv.className = "green";  // 결과 색상 변경
        } else {
            resultDiv.textContent = "파일 저장에 실패했습니다.";
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
