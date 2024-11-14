let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let nativeAudioPreview = document.getElementById("native-audio-preview");
let countdownText = document.getElementById('countdown'); // 카운트다운을 표시할 요소

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// 페이지 로드 후 음성을 준비만 하고 자동으로 재생되지 않도록 설정
window.onload = function () {
    nativeAudioPreview.load();  // 음성을 로드만 시킴 (자동 재생 X)
    console.log("페이지가 로드되었습니다.");
};

// 오디오 재생을 위한 함수 (Play 버튼을 눌렀을 때)
function playNativeAudio() {
    nativeAudioPreview.play();  // 버튼 클릭 시 음성 재생
    console.log("원어민 발음 오디오 재생 시작");
}

// 카운트다운 시작
function startCountdown() {
    countdownText.style.display = 'block'; // 카운트다운 영역을 보이게 설정
    console.log("카운트다운 시작");

    let countdownNumbers = [3, 2, 1];
    let index = 0;

    function updateCountdown() {
        if (index < countdownNumbers.length) {
            countdownText.innerText = countdownNumbers[index];
            console.log(`카운트다운: ${countdownNumbers[index]}`);
            index++;
            setTimeout(updateCountdown, 1000); // 1초마다 숫자 변경
        } else {
            countdownText.innerText = '녹음을 시작하세요'; // 안내 문구 표시
            console.log("녹음을 시작하세요 안내 문구 표시");
            setTimeout(() => {
                countdownText.style.display = 'none'; // 안내 문구 숨기기
                startRecording(); // 녹음 시작
            }, 1000); // 안내 문구가 1초 동안 표시된 후 녹음 시작
        }
    }

    updateCountdown(); // 카운트다운 시작
}

// 녹음 시작
function startRecording() {
    console.log("녹음 시작 함수 호출");

    if (navigator.mediaDevices) {
        audioData = [];

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                console.log("마이크 스트림을 받았습니다.");
                audioStream = stream;
                recorder = new MediaRecorder(stream);

                recorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioData.push(event.data);
                        console.log("녹음 데이터 수집 중...");
                    }
                };

                recorder.onstop = () => {
                    if (audioData.length > 0) {
                        console.log("녹음이 종료되었습니다.");
                        processRecording();
                    } else {
                        console.log("녹음 데이터가 없습니다.");
                        alert("녹음 데이터가 없습니다. 다시 시도해주세요.");
                    }
                };

                recorder.start(); // 녹음 시작
                console.log("녹음 시작됨");

                // 버튼 상태 변경
                document.getElementById("micButton").disabled = true; // 마이크 버튼 비활성화
                document.getElementById("stopBtn").disabled = false; // 녹음 종료 버튼 활성화

                // 추가로 마이크 버튼을 텍스트나 스타일로 변경
                document.getElementById("micButton").innerText = "녹음 중...";
            })
            .catch(err => {
                console.log("Audio error: " + err); // 에러 출력
                alert("녹음 시작에 실패했습니다. 마이크 권한을 확인해주세요.");
            });
    } else {
        console.log("getUserMedia를 지원하지 않는 브라우저입니다.");
        alert("getUserMedia를 지원하지 않는 브라우저입니다.");
    }
}

// 녹음 종료
function stopRecording() {
    if (recorder && recorder.state === 'recording') {
        recorder.stop();
        console.log("녹음 종료");
        audioStream.getTracks().forEach(track => track.stop()); // 마이크 종료

        // 버튼 상태 변경
        document.getElementById("micButton").disabled = false; // 마이크 버튼 활성화
        document.getElementById("stopBtn").disabled = true; // 녹음 종료 버튼 비활성화
        document.getElementById("micButton").innerText = "녹음 시작"; // 텍스트 변경
    } else {
        console.log("이미 녹음이 종료되었습니다.");
    }
}

// 녹음 처리
function processRecording() {
    const audioBlob = new Blob(audioData, { type: 'audio/wav' });
    console.log("녹음 데이터 처리 중...");
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    formData.append('target_word', currentWord);

    fetch('/pron_practice/evaluate_pronunciation/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log("서버로부터 응답 받음");
            const score = data.score;
            const feedback = data.feedback;
            displayFeedback(score, feedback);

            const audioUrl = URL.createObjectURL(audioBlob);
            audioPreview.src = audioUrl;
            audioPreview.style.display = 'block';
        })
        .catch(error => {
            console.error("Error processing recording: ", error);
            alert("서버 처리 중 오류가 발생했습니다.");
        });
}

// 피드백 표시
function displayFeedback(score, feedback) {
    console.log("피드백 표시 중...");
    document.getElementById("score").textContent = score;
    document.getElementById("score-bar").style.width = score + "%";

    const feedbackSection = document.getElementById("feedback-section");
    const feedbackDisplay = document.getElementById("feedback");
    feedbackDisplay.textContent = feedback;
    feedbackSection.style.display = 'block';

    const progressBar = document.getElementById('score-bar');
    if (score >= 80) {
        progressBar.className = 'green';
    } else if (score >= 60) {
        progressBar.className = 'yellow';
    } else {
        progressBar.className = 'red';
    }
}

// 다음 단어로 이동
function nextWord() {
    console.log("다음 단어로 이동");
    window.location.href = '/pron_practice/next_word/';
}

// 연습 종료
function exitPractice() {
    console.log("연습 종료");
    window.location.href = '/';
}
