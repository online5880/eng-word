let recorder;
let audioStream;
let audioData = [];
let audioPreview = document.getElementById("audio-preview");

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// 녹음 시작
function startRecording() {
    console.log("startRecording 호출됨");  // 녹음 시작 함수 호출 확인

    if (navigator.mediaDevices) {
        audioData = [];
        console.log("마이크 접근 시도 중...");

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                recorder = new MediaRecorder(stream);

                console.log("녹음기 시작됨");

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

// 녹음 중지
function stopRecording() {
    console.log("stopRecording 호출됨");  // 녹음 중지 함수 호출 확인

    if (recorder && recorder.state === 'recording') {
        recorder.stop();
        audioStream.getTracks().forEach(track => track.stop()); // 마이크 종료

        console.log("녹음 중지됨");
        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    } else {
        console.log("녹음이 진행 중이 아닙니다.");
    }
}

// 녹음 처리
function processRecording() {
    console.log("processRecording 호출됨");  // 녹음 처리 함수 호출 확인

    const audioBlob = new Blob(audioData, { type: 'audio/wav' });
    console.log("오디오 Blob 생성됨, 크기: " + audioBlob.size);

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
            console.log("서버 응답: ", data);  // 서버 응답 확인

            const resultDiv = document.getElementById("audio-result");

            if (data.transcript) {
                console.log("음성 인식 결과: " + data.transcript);  // 음성 인식 결과 확인
                resultDiv.textContent = "음성 인식 결과: " + data.transcript;
                resultDiv.className = "green";
            } else {
                console.log("음성 인식 실패");
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