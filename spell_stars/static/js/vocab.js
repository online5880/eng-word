let mediaRecorder;
let recordedChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                recordedChunks = [];
                const audioURL = URL.createObjectURL(audioBlob);
                document.getElementById('recorded-audio').src = audioURL;

                // Send the recorded audio to the server for evaluation
                sendAudioToServer(audioBlob);
            };
            mediaRecorder.start();
        })
        .catch(error => {
            console.error("Microphone access denied", error);
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
}

function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(`Your pronunciation score: ${data.score}`);
        document.getElementById('pronunciation_level').value = data.score;

        // Check if the pronunciation meets the threshold
        if (data.score >= 80) { // Example threshold
            document.getElementById('next-word-container').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
