document.addEventListener("DOMContentLoaded", function () {
    const micButton = document.getElementById("micButton");
    const statusMessage = document.getElementById("statusMessage");
    const studentCorrectnessBox = document.getElementById("studentCorrectnessBox");
    const aiCorrectnessBox = document.getElementById("aiCorrectnessBox");
    const studentAccuracyBox = document.getElementById("studentAccuracyBox");
    const aiAccuracyBox = document.getElementById("aiAccuracyBox");
    const uploadAudioUrl = "/sent/upload_audio/"; // 서버 API 경로
    const nextQuestionUrl = "/sent/next_question/"; // 다음 문제로 이동 경로
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

                    // 학생 및 AI 정오답 상태 업데이트
                    studentCorrectnessBox.textContent = response.is_correct ? "정답" : "오답";
                    aiCorrectnessBox.textContent = response.ai_correct ? "정답" : "오답";

                    // 정답률 업데이트
                    studentAccuracyBox.textContent = `학생 정답률: ${response.student_accuracy.toFixed(2)}%`;
                    aiAccuracyBox.textContent = `AI 정답률: ${response.ai_accuracy.toFixed(2)}%`;

                    // 상태 메시지 업데이트
                    statusMessage.textContent = response.message;

                    // 다음 문제로 이동
                    if (response.next_question_available) {
                        setTimeout(() => loadNextQuestion(), 2000);
                    } else {
                        statusMessage.textContent = "모든 문제를 완료했습니다!";
                    }

                    // 녹음 상태 초기화
                    isRecording = false;
                    micButton.disabled = false;
                    micButton.textContent = "녹음 시작";
                } catch (error) {
                    statusMessage.textContent = "오디오 업로드 중 오류 발생: " + error.message;
                }
            };

            // 녹음 시작
            mediaRecorder.start();
            isRecording = true;
            micButton.disabled = true;
            micButton.textContent = "녹음 중...";
            statusMessage.textContent = "녹음 중...";
        } catch (error) {
            statusMessage.textContent = "마이크 접근 오류";
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

        const response = await fetch(uploadAudioUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken,
            },
        });

        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`서버 오류: ${response.status}`);
        }
    }

    /**
     * 다음 문제 로드 함수
     */
    async function loadNextQuestion() {
        try {
            const response = await fetch(nextQuestionUrl, {
                method: "GET",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").content,
                },
            });

            if (response.ok) {
                const newPage = await response.text();
                document.body.innerHTML = newPage;
            } else {
                throw new Error("문제를 불러오는 데 실패했습니다.");
            }
        } catch (error) {
            statusMessage.textContent = "다음 문제로 이동 중 오류 발생: " + error.message;
        }
    }
});
