// DOM 요소들
const micButton = document.getElementById("micButton");
const statusText = document.getElementById("statusText");
const progressFill = document.getElementById("progressFill");
const audioPreview = document.getElementById("audio-preview");
const resultText = document.getElementById("audio-result");

// 변수들
let recorder;
let audioStream;
let audioData = [];
let isRecording = false;

// 마이크 버튼 클릭 시 녹음 시작 또는 중지
micButton.addEventListener("click", () => {
    if (isRecording) {
        stopRecording();  // 녹음 중이면 중지
    } else {
        startRecording();  // 녹음 시작
    }
});

// 녹음 시작 함수
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
                    if (event.data.size > 0) {
                        audioData.push(event.data);
                    }
                };
                recorder.onstop = () => {
                    if (audioData.length > 0) {
                        processRecording();  // 녹음이 완료되면 처리 함수 호출
                    } else {
                        alert("녹음 데이터가 없습니다. 다시 시도해주세요.");
                    }
                };
                recorder.start();
                isRecording = true;
                updateUIForRecording();  // UI 상태 업데이트
            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("마이크 권한을 확인해주세요.");
            });
    } else {
        alert("이 브라우저는 오디오 녹음을 지원하지 않습니다.");
    }
}

// 녹음 중지 함수
function stopRecording() {
    console.log("stopRecording 호출됨");
    if (recorder && recorder.state === "recording") {
        recorder.stop();
        audioStream.getTracks().forEach(track => track.stop());  // 모든 트랙 중지
        isRecording = false;
        updateUIForStopped();  // UI 상태 업데이트
    }
}

// 녹음이 완료되면 서버로 전송
function processRecording() {
    const blob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("audio_file", blob, "audio.wav");

    // 서버로 전송
    fetch(`/recognize_audio/${window.sentenceId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,  // CSRF 토큰
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("음성 인식 오류가 발생했습니다.");
        } else {
            displayResult(data);  // 음성 인식 결과 표시
        }
    })
    .catch(error => {
        console.log("서버 오류:", error);
        alert("서버 처리 중 오류가 발생했습니다.");
    });
}

// 음성 인식 결과 표시 함수
function displayResult(data) {
    resultText.textContent = `Transcript: ${data.transcript}`;
    audioPreview.style.display = "block";
    audioPreview.src = data.audio_url;  // 성공/실패 피드백 오디오

    if (data.is_correct) {
        resultText.className = "green";
        alert("정답입니다!");
    } else {
        resultText.className = "red";
        resultText.textContent += ` (정답: ${data.correct_answer})`;
        alert(`틀렸습니다. 정답은 ${data.correct_answer}입니다.`);
    }
}

// UI 업데이트 함수 (녹음 중 상태)
function updateUIForRecording() {
    micButton.innerHTML = '<div class="mic-icon"><i class="fas fa-stop"></i></div>'; // 마이크 아이콘을 중지 아이콘으로 변경
    statusText.textContent = "녹음 중...";  // 상태 텍스트
    progressFill.style.width = "0";  // 프로그레스 바 초기화
    voiceLevelFill.style.width = "0";  // 음성 레벨 초기화
    micAnimation.style.display = "block";  // 애니메이션 시작
    progressBarAnimation();  // 프로그레스 바 애니메이션
}

// UI 업데이트 함수 (녹음 중지 후 상태)
function updateUIForStopped() {
    micButton.innerHTML = '<div class="mic-icon"><i class="fas fa-microphone"></i></div>'; // 마이크 아이콘으로 변경
    statusText.textContent = "녹음이 완료되었습니다. 결과를 확인하세요.";  // 상태 텍스트
    micAnimation.style.display = "none";  // 애니메이션 종료
}


// 프로그레스 바 애니메이션
function progressBarAnimation() {
    let progress = 0;
    const interval = setInterval(() => {
        if (progress >= 100) {
            clearInterval(interval);
        } else {
            progress += 1;
            progressFill.style.width = progress + "%";
        }
    }, 100);
}
