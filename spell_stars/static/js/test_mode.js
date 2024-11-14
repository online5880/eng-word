let recorder;
let audioStream;
let audioData = [];

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
                document.getElementById("micButton").disabled = true;  // 시작 버튼 비활성화
                document.getElementById("micButton").classList.add("active");  // 애니메이션 효과 활성화
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
        document.getElementById("micButton").disabled = false;  // 중지 버튼 활성화
        document.getElementById("micButton").classList.remove("active");  // 애니메이션 효과 제거
        console.log("녹음 중지됨");
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
    fetch(`/test_mode/submit_audio/`, {  // test_mode로 경로 수정
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
                if (data.transcript && window.currentWord) {
                    const isCorrect = data.transcript.toLowerCase() === window.currentWord.toLowerCase();
                    const resultElement = document.getElementById("audio-result");

                    // 피드백 출력
                    if (isCorrect) {
                        resultElement.className = "green";  // 정답일 때
                        resultElement.textContent = "정답입니다!";
                    } else {
                        resultElement.className = "red";  // 틀렸을 때
                        resultElement.textContent = `틀렸습니다. 정답은 ${window.currentWord}입니다.`;
                    }

                    // 점수와 피드백 표시
                    displayScoreFeedback(isCorrect);

                } else {
                    console.log("Transcript 또는 currentWord가 없음");
                    alert("서버에서 음성 인식 결과를 받지 못했습니다.");
                }
                resetButtons();
            }
        })
        .catch(error => {
            console.log("Error during audio upload:", error);
            alert("서버 처리 중 오류가 발생했습니다.");
            resetButtons();  // 버튼 초기화
        });
}

// 점수와 피드백 표시
function displayScoreFeedback(isCorrect) {
    const scoreElement = document.getElementById("score");
    const feedbackElement = document.getElementById("feedback");
    const nextButton = document.getElementById("next-question-btn");

    let score = isCorrect ? 100 : 0;  // 정답이면 100점, 틀리면 0점
    scoreElement.textContent = score;
    feedbackElement.textContent = isCorrect ? "정답!" : "틀렸습니다. 다시 시도하세요.";

    // 점수에 따라 피드백 스타일 설정
    const progressBar = document.getElementById("score-bar");
    progressBar.style.width = score + "%";
    if (score >= 80) {
        progressBar.className = "green";
    } else if (score >= 60) {
        progressBar.className = "yellow";
    } else {
        progressBar.className = "red";
    }

    // 다음 문제로 이동하는 버튼 활성화
    nextButton.disabled = false;
}

// 버튼 상태 초기화
function resetButtons() {
    document.getElementById("micButton").disabled = false;  // 시작 버튼 활성화
    document.getElementById("micButton").classList.remove("active");  // 애니메이션 효과 제거
    const nextButton = document.getElementById("next-question-btn");
    if (nextButton) {
        nextButton.disabled = true;  // 다음 문제로 버튼 비활성화
    }
}

// 다음 문제로 이동
function nextQuestion() {
    console.log("다음 문제로 이동");
    fetch('/test_mode/next_question/', {  // nextQuestion로 경로 수정
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.sentence) {
            // 새로운 문제로 업데이트
            document.getElementById("sentence").textContent = data.sentence;
            document.getElementById("current-word").textContent = data.word;
            // 다음 문제의 ID를 세션에 저장하는 등의 추가 작업 가능
            resetButtons();  // 버튼 초기화
        } else {
            console.log('새 문제를 가져오지 못했습니다.');
        }
    })
    .catch(error => {
        console.error('AJAX 요청 오류:', error);
    });
}


// 이벤트 리스너 추가
const nextQuestionButton = document.getElementById("next-question-btn");
if (nextQuestionButton) {
    nextQuestionButton.addEventListener('click', nextQuestion);
}
