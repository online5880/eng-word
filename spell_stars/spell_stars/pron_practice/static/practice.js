let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;
let audioPreview = document.getElementById("audio-preview");
let nativeAudioPreview = document.getElementById("native-audio-preview");  // 원어민 음성 미리보기

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// 원어민 음성 재생
function loadNativeAudio() {
    let nativeAudioUrl = '/media/audio/native/eraser_a.wav';  // 수정된 경로
    nativeAudioPreview.src = nativeAudioUrl;
    nativeAudioPreview.style.display = 'block';
    nativeAudioPreview.load();  // 음성 파일 로드
    nativeAudioPreview.play();  // 자동 재생
}

// 녹음 시작
function startRecording() {
    if (navigator.mediaDevices) {
        // 녹음 시작 시 오디오 데이터 초기화
        audioData = [];

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                recorder = new MediaRecorder(stream);

                recorder.ondataavailable = event => audioData.push(event.data);
                recorder.onstop = processRecording;
                recorder.start();

                document.getElementById("startBtn").disabled = true;
                document.getElementById("stopBtn").disabled = false;
            })
            .catch(err => {
                console.log("Audio error: " + err);
                alert("녹음 시작에 실패했습니다. 마이크 권한을 확인해주세요.");
            });
    }
}

// 녹음 종료
function stopRecording() {
    if (recorder && recorder.state === 'recording') {
        recorder.stop();
        audioStream.getTracks().forEach(track => track.stop());

        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
}

// 녹음 처리
function processRecording() {
    const audioBlob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    formData.append('target_word', currentWord);  // 목표 단어를 포함시킴

    // 음성 파일을 서버로 전송하여 평가받기
    fetch('/pron_practice/evaluate_pronunciation/', {  // 발음 평가를 위한 API 경로
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken // CSRF 토큰을 헤더에 포함
        }
    })
        .then(response => response.json())  // 응답을 JSON으로 받음
        .then(data => {
            const score = data.score;
            const feedback = data.feedback;
            displayFeedback(score, feedback);

            // 녹음한 음성 미리보기 (자동 재생 없음)
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
    document.getElementById("score").textContent = score;
    document.getElementById("score-bar").style.width = score + "%";

    // 피드백 텍스트 표시
    const feedbackSection = document.getElementById("feedback-section");
    const feedbackDisplay = document.getElementById("feedback");
    feedbackDisplay.textContent = feedback;
    feedbackSection.style.display = 'block';

    // 진행 바 색상 변경 (점수에 따라)
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
    window.location.href = '/pron_practice/next_word/';
}

// 연습 종료
function exitPractice() {
    window.location.href = '/';
}

// 페이지 로드 시 원어민 음성 로드
window.onload = function () {
    loadNativeAudio();  // 원어민 음성 로드 및 자동 재생
}
