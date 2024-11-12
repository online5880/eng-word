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
                        processRecording();  // 녹음이 완료되면 처리 함수 호출
                    } else {
                        console.log("녹음 데이터가 없습니다.");
                        alert("녹음 데이터가 없습니다. 다시 시도해주세요.");
                        resetButtons();  // 버튼 초기화
                    }
                };
                // 녹음 시작
                recorder.start();
                document.getElementById("startBtn").disabled = true;  // 시작 버튼 비활성화
                document.getElementById("stopBtn").disabled = false;  // 중지 버튼 활성화
            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("마이크 권한을 확인해주세요.");
                resetButtons();  // 버튼 초기화
            });
    } else {
        alert("이 브라우저는 오디오 녹음을 지원하지 않습니다.");
    }
}
// 녹음 중지
function stopRecording() {
    console.log("stopRecording 호출됨");
    if (recorder && recorder.state === "recording") {
        recorder.stop();  // 녹음 중지
        audioStream.getTracks().forEach(track => track.stop());  // 모든 트랙 중지
        document.getElementById("stopBtn").disabled = true;  // 중지 버튼 비활성화
        console.log("녹음 중지됨");
        // 버튼 재활성화
        document.getElementById("startBtn").disabled = true;  // 처리 중이라 시작 버튼 비활성화
    } else {
        console.log("녹음이 진행 중이 아닙니다.");
    }
}
// 음성 파일 처리 및 서버 전송
function processRecording() {
    console.log("processRecording 호출됨");
    const blob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("audio_file", blob, "audio.wav");
    // 서버로 전송
    fetch(`recognize_audio/${window.questionId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,  // CSRF 토큰 포함
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                resetButtons();  // 버튼 초기화
            } else {
                console.log("Transcript: ", data.transcript);
                console.log("현재 문제 단어 (currentWord): ", window.currentWord);
                // transcript와 currentWord가 존재하는지 확인
                if (data.transcript && window.currentWord) {
                    // `window.currentWord`와 비교하여 정답 여부 확인
                    const isCorrect = data.transcript.toLowerCase() === window.currentWord.toLowerCase();
                    document.getElementById("audio-result").textContent = `Transcript: ${data.transcript}`;
                    // 정오답 확인
                    if (isCorrect) {
                        document.getElementById("audio-result").className = "green";  // 정답일 때
                        alert("정답입니다!");
                    } else {
                        document.getElementById("audio-result").className = "red";  // 틀렸을 때
                        document.getElementById("audio-result").textContent += ` (정답: ${window.currentWord})`;
                        alert(`틀렸습니다. 정답은 ${window.currentWord}입니다.`);
                    }
                    // 음성 파일 URL로 음성 미리듣기
                    audioPreview.style.display = "block";
                    audioPreview.src = data.audio_url;  // 서버에서 반환된 URL을 사용
                } else {
                    console.log("Transcript 또는 currentWord가 없음");
                    alert("서버에서 음성 인식 결과를 받지 못했습니다.");
                }
                // 처리 완료 후 시작 버튼 재활성화
                resetButtons();
            }
        })
        .catch(error => {
            console.log("Error during audio upload:", error);
            alert("서버 처리 중 오류가 발생했습니다.");
            resetButtons();  // 버튼 초기화
        });
}
// 버튼 상태 초기화
function resetButtons() {
    document.getElementById("startBtn").disabled = false;  // 시작 버튼 활성화
    document.getElementById("stopBtn").disabled = true;  // 중지 버튼 비활성화
}