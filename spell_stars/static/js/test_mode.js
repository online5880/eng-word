let recorder;
let audioStream;
let audioData = [];
let audioPreview = document.getElementById("audio-preview");

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

                recorder.start(); // 녹음 시작
                document.getElementById("startBtn").disabled = true;
                document.getElementById("stopBtn").disabled = false;
            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("녹음 시작에 실패했습니다. 마이크 권한을 확인해주세요.");
            });
    }
}

// 녹음 중지
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

    fetch(`/recognize_audio/${questionId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById("audio-result");

        if (data.transcript) {
            resultDiv.textContent = "음성 인식 결과: " + data.transcript;
            resultDiv.className = "green";
        } else {
            resultDiv.textContent = "음성 인식에 실패했습니다.";
            resultDiv.className = "red";
        }

        const audioUrl = URL.createObjectURL(audioBlob);
        audioPreview.src = audioUrl;
        audioPreview.style.display = 'block';
    })
    .catch(error => {
        console.error("Error processing recording: ", error);
        alert("서버 처리 중 오류가 발생했습니다.");
    });
}
