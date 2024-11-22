document.addEventListener("DOMContentLoaded", function () {
    const micButton = document.getElementById("micButton");
    const statusText = document.getElementById("statusMessage");
    const studentCorrectnessBox = document.getElementById("studentCorrectnessBox");
    const aiCorrectnessBox = document.getElementById("aiCorrectnessBox");
    const studentAccuracyBox = document.getElementById("studentAccuracyBox");
    const aiAccuracyBox = document.getElementById("aiAccuracyBox");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    const uploadAudioUrl = "/sent/upload_audio/";
    const nextQuestionUrl = "/sent/next_question/";
    const hiddenWord = document.getElementById("hiddenWord").value.trim();
    console.log("Hidden Word:", hiddenWord);
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];

    async function startRecording() {
        try {
            console.log("Starting recording...");
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
    
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                const formData = new FormData();
                formData.append("audio", audioBlob);
                formData.append("word", hiddenWord);

                try {
                    const response = await fetch(uploadAudioUrl, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                        },
                        body: formData,
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log("Upload success:", data);
                        updateResults(data);
                    } else {
                        console.error("Server error:", response.status);
                        statusText.textContent = "오류: 서버와의 통신에 실패했습니다.";
                    }
                } catch (error) {
                    console.error("Upload failed:", error);
                    statusText.textContent = "오류: 파일 업로드 중 문제가 발생했습니다.";
                }
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add("recording");
            statusText.textContent = "녹음 중...";
        } catch (error) {
            console.error("Microphone access error:", error);
            statusText.textContent = `오류: 마이크에 접근할 수 없습니다. (${error.message})`;
        }
    }

    function stopRecording() {
        if (isRecording && mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach((track) => track.stop());
            isRecording = false;
            micButton.classList.remove("recording");
            statusText.textContent = "녹음이 완료되었습니다.";
        } else {
            console.warn("No active recording to stop.");
        }
    }

    function updateResults(data) {
        if (data.redirect) {
            window.location.href = data.redirect; // 결과 페이지로 이동
        } else {
            studentCorrectnessBox.textContent = data.is_correct ? "정답" : "오답";
            aiCorrectnessBox.textContent = data.ai_correct ? "정답" : "오답";
            studentAccuracyBox.textContent = `학생 정답률: ${(data.student_accuracy * 100).toFixed(2)}%`;
            aiAccuracyBox.textContent = `AI 정답률: ${(data.ai_accuracy * 100).toFixed(2)}%`;
            statusText.textContent = data.is_correct ? "정답입니다!" : "오답입니다. 다시 시도하세요.";
    
            // 일정 시간 후 다음 문제 로드
            setTimeout(() => {
                loadNextQuestion(); // 다음 문제 비동기 로드
            }, 2000); // 2초 후 이동
        }
    }
    

    async function loadNextQuestion() {
        console.log("Loading next question...");
        try {
            const response = await fetch("/sent/next_question/", {
                method: "GET",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            });
    
            if (response.ok) {
                const questionData = await response.json();
                console.log("Next question data:", questionData);
                updateQuestionUI(questionData); // 화면 갱신
            } else {
                console.error("Failed to fetch next question:", response.status, response.statusText);
                statusText.textContent = "오류: 다음 문제를 불러오지 못했습니다.";
            }
        } catch (error) {
            console.error("Next question loading error:", error);
            statusText.textContent = "오류: 다음 문제를 불러오는 중 문제가 발생했습니다.";
        }
    }
    

    function updateQuestionUI(questionData) {
        // DOM 요소 선택
        const questionText = document.querySelector(".question-container p:nth-child(2)");
        const meaningText = document.querySelector(".question-container p:nth-child(3)");
        const hiddenWordInput = document.getElementById("hiddenWord");
        const statusText = document.getElementById("statusMessage");
        const studentCorrectnessBox = document.getElementById("studentCorrectnessBox");
        const aiCorrectnessBox = document.getElementById("aiCorrectnessBox");
        const studentAccuracyBox = document.getElementById("studentAccuracyBox");
        const aiAccuracyBox = document.getElementById("aiAccuracyBox");
    
        // 데이터 검증
        if (!questionData || !questionData.sentence || !questionData.meaning || !questionData.word) {
            statusText.textContent = "오류: 올바른 문제 데이터를 가져오지 못했습니다.";
            console.error("Invalid question data:", questionData);
            return;
        }
    
        // 문제와 뜻 갱신
        if (questionText) {
            questionText.textContent = `문장: ${questionData.sentence}`;
        } else {
            console.error("Error: Question text DOM element not found.");
        }
    
        if (meaningText) {
            meaningText.textContent = `뜻: ${questionData.meaning}`;
        } else {
            console.error("Error: Meaning text DOM element not found.");
        }
    
        // Hidden input 값 갱신
        if (hiddenWordInput) {
            hiddenWordInput.value = questionData.word;
        } else {
            console.error("Error: Hidden input DOM element not found.");
        }
    
        // 상태 초기화
        if (statusText) {
            statusText.textContent = "새로운 문제입니다. 녹음을 시작하세요!";
        } else {
            console.error("Error: Status text DOM element not found.");
        }
    
        if (studentCorrectnessBox) {
            studentCorrectnessBox.textContent = "";
        } else {
            console.error("Error: Student correctness box DOM element not found.");
        }
    
        if (aiCorrectnessBox) {
            aiCorrectnessBox.textContent = "";
        } else {
            console.error("Error: AI correctness box DOM element not found.");
        }
    
        if (studentAccuracyBox) {
            studentAccuracyBox.textContent = "";
        } else {
            console.error("Error: Student accuracy box DOM element not found.");
        }
    
        if (aiAccuracyBox) {
            aiAccuracyBox.textContent = "";
        } else {
            console.error("Error: AI accuracy box DOM element not found.");
        }
    }
    

    micButton.addEventListener("click", () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });
});
