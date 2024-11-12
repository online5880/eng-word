let recorder;
let audioStream;
let audioData = [];
let audioPreview = document.getElementById("audio-preview");

// 녹음 시작
function startRecording() {
    console.log("startRecording 호출됨");

    if (navigator.mediaDevices) {
        audioData = [];
        console.log("마이크 접근 시도 중...");

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                recorder = new MediaRecorder(stream);

                recorder.ondataavailable = event => {
                    console.log("ondataavailable 호출됨, 크기: " + event.data.size);
                    if (event.data.size > 0) {
                        audioData.push(event.data);
                    }
                };

                recorder.onstop = () => {
                    console.log("녹음 종료됨");
                    if (audioData.length > 0) {
                        processRecording();
                    } else {
                        console.log("녹음 데이터가 없습니다.");
                        alert("녹음 데이터가 없습니다. 다시 시도해주세요.");
                    }
                };

                // 녹음 시작
                recorder.start();
                document.getElementById("startBtn").disabled = true;
                document.getElementById("stopBtn").disabled = false;
            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("마이크 권한을 확인해주세요.");
            });
    } else {
        alert("이 브라우저는 오디오 녹음을 지원하지 않습니다.");
    }
}

// 녹음 중지
function stopRecording() {
    console.log("stopRecording 호출됨");
    recorder.stop();
    audioStream.getTracks().forEach(track => track.stop()); // 모든 트랙 중지
    document.getElementById("stopBtn").disabled = true;
}

// 음성 파일 처리 및 서버 전송
function processRecording() {
    const blob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("audio_file", blob, "audio.wav");

    // 서버로 전송
    fetch(`recognize_audio/${window.questionId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken, // CSRF 토큰 포함
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                console.log("Transcript: ", data.transcript);
                document.getElementById("audio-result").textContent = `Transcript: ${data.transcript}`;

                // 음성 파일 URL로 음성 미리듣기
                audioPreview.style.display = "block";
                audioPreview.src = data.audio_url;  // 반환된 URL을 사용
            }
        })
        .catch(error => console.log("Error during audio upload:", error));
}