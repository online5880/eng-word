document.addEventListener("DOMContentLoaded", function () {
    const micButton = document.getElementById("micButton");
    const statusMessage = document.getElementById("statusMessage");
    const studentCorrectnessBox = document.getElementById("studentCorrectnessBox");
    const uploadAudioUrl = "/sent/upload_audio/"; // 올바른 경로 확인
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];

    /**
     * 녹음 시작 함수
     */
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            // 녹음 데이터 수집
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

            // 녹음 종료 시 처리
            mediaRecorder.onstop = async () => {
                try {
                    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                    const currentWord = document.getElementById("hiddenWord").value.trim();

                    // 오디오 업로드
                    const response = await uploadAudio(audioBlob, currentWord);

                    // 서버 응답 처리
                    studentCorrectnessBox.textContent = response.is_correct
                        ? "정답"
                        : "오답";
                    statusMessage.textContent = response.message;

                    // 녹음 상태 초기화
                    isRecording = false;
                    micButton.disabled = false;
                    micButton.textContent = "녹음 시작";
                } catch (error) {
                    statusMessage.textContent = "오디오 업로드 중 오류 발생: " + error.message;
                    console.error("Error uploading audio:", error);
                }
            };

            // 녹음 시작
            mediaRecorder.start();
            isRecording = true;
            micButton.disabled = true;
            micButton.textContent = "녹음 중...";
            statusMessage.textContent = "녹음 중...";
        } catch (error) {
            statusMessage.textContent = "마이크에 접근할 수 없습니다.";
            console.error("Error accessing microphone:", error);
        }
    }

    /**
     * 녹음 종료 및 업로드 트리거
     */
    micButton.addEventListener("click", () => {
        if (isRecording) {
            mediaRecorder.stop();
            statusMessage.textContent = "녹음 완료. 서버로 전송 중...";
        } else {
            audioChunks = [];
            startRecording();
        }
    });

    /**
     * 오디오 업로드 함수
     * @param {Blob} audioBlob - 녹음된 오디오 Blob 데이터
     * @param {string} word - 현재 단어
     * @returns {Object} 서버 응답 데이터(JSON)
     */
    async function uploadAudio(audioBlob, word) {
        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("word", word);

        // CSRF 토큰 가져오기
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").content;

        // 서버로 POST 요청
        const response = await fetch(uploadAudioUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken, // CSRF 토큰 포함
            },
        });

        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Network response was not ok: ${response.status}`);
        }
    }
});
