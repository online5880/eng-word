let recorder;
let audioStream;
let audioData = [];
let currentWord = document.getElementById("current-word").textContent;

function startRecording() {
    if (navigator.mediaDevices) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                recorder = new MediaRecorder(stream);
                recorder.ondataavailable = event => audioData.push(event.data);
                recorder.onstop = processRecording;
                recorder.start();
            })
            .catch(err => console.log("Audio error: " + err));
  }
}

function stopRecording() {
    recorder.stop();
    audioStream.getTracks().forEach(track => track.stop());
}

function processRecording() {
    const audioBlob = new Blob(audioData, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    formData.append('target_word', currentWord);  // 목표 단어를 포함시킴
    
    // 음성 파일을 서버로 전송하여 평가받기
    fetch('/evaluate_pronunciation/', {  // 발음 평가를 위한 API 경로
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const score = data.score;
        displayFeedback(score);
    })
    .catch(error => console.error("Error processing recording: ", error));
}

function displayFeedback(score) {
    document.getElementById("score").textContent = score;
    document.getElementById("score-bar").style.width = score + "%";
}

function nextWord() {
    window.location.href = '/pron_practice/next_word/';
}

function exitPractice() {
    window.location.href = '/';
}
