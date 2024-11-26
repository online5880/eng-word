document.addEventListener("DOMContentLoaded", function () {
    const micButton = document.getElementById("micButton");
    const statusText = document.getElementById("statusMessage");
    const studentCorrectnessBox = document.getElementById("studentCorrectnessBox");
    const aiCorrectnessBox = document.getElementById("aiCorrectnessBox");
    const studentAccuracyBox = document.getElementById("studentAccuracyBox");
    const aiAccuracyBox = document.getElementById("aiAccuracyBox");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    const uploadAudioUrl = "/sent/upload_audio/";
    const nextQuestionButton = document.getElementById("nextQuestionButton");
    const hiddenWord = document.getElementById("hiddenWord").value.trim();
    console.log("Hidden Word:", hiddenWord);
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let startTime = null; // 녹음 시작 시간
    let endTime = null; // 녹음 종료 시간   
    
    function showAiThinking() {
        const aiThinkingContainer = document.getElementById("aiThinkingContainer");
        const aiProgressFill = document.getElementById("aiProgressFill");
    
        console.log("AI 게이지바 표시");
        aiThinkingContainer.style.display = "block";
        aiProgressFill.style.width = "0%"; // 초기화
    
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10; // 게이지 증가 속도
            aiProgressFill.style.width = `${progress}%`;
    
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 300); // 0.3초마다 업데이트
    }
    
    function updateAiProgress(duration) {
        const aiProgressFill = document.getElementById("aiProgressFill");
    
        // 응답 시간이 duration인 경우 애니메이션으로 게이지 채움
        aiProgressFill.style.transition = `width ${duration}s ease-in-out`;
        aiProgressFill.style.width = "100%"; // 게이지를 끝까지 채움
    }
    
    function resetAiProgress() {
        const aiProgressFill = document.getElementById("aiProgressFill");
    
        // 게이지 바 초기화
        aiProgressFill.style.transition = "none";
        aiProgressFill.style.width = "0%";
    }

    async function startRecording() {
        try {
            console.log("Starting recording...");
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
    
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstart = () => {
                startTime = new Date().getTime(); // 녹음 시작 시간 기록
                console.log("Recording started at:", startTime);

            };
            mediaRecorder.onstop = async () => {
                // 게이지 바 항상 표시
                showAiThinking();
            
                // 요청 시작 시간 기록
                const fetchStartTime = new Date().getTime();
                
                try {
                    endTime = new Date().getTime();
                    console.log("Recording stopped at:", endTime);
            
                    const studentTime = (endTime - startTime) / 1000;
                    console.log("Student response time:", studentTime, "seconds");
            
                    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                    const formData = new FormData();
                    formData.append("audio", audioBlob);
                    formData.append("word", hiddenWord);
                    formData.append("student_time", studentTime);
            
                    const response = await fetch(uploadAudioUrl, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                        },
                        body: formData,
                    });
            
                    const fetchEndTime = new Date().getTime(); // 요청 완료 시간 기록
                    const fetchDuration = (fetchEndTime - fetchStartTime) / 1000; // 응답 시간 계산
                    console.log("Fetch duration:", fetchDuration, "seconds");
            
                    // 응답 시간에 맞춰 게이지 바 애니메이션
                    updateAiProgress(fetchDuration);
            
                    if (response.ok) {
                        const data = await response.json();
                        console.log("Upload success:", data);
                        // AI 상태 텍스트 변경
                        const aiThinkingText = document.getElementById("aiThinkingText");
                        aiThinkingText.textContent = "AI가 정답을 제출했습니다";
            
                        setTimeout(() => {
                            resetAiProgress(); // 게이지 바 초기화
                            updateResults(data); // 결과 업데이트
                        }, fetchDuration * 1000); // 애니메이션 완료 후 초기화
                    } else {
                        console.error("Server error:", response.status);
                        statusText.textContent = "오류: 서버와의 통신에 실패했습니다.";
                        setTimeout(resetAiProgress, fetchDuration * 1000);
                    }
                } catch (error) {
                    console.error("Upload failed:", error);
                    statusText.textContent = "오류: 파일 업로드 중 문제가 발생했습니다.";
                    resetAiProgress(); // 게이지 바 초기화
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
            console.log("Redirecting to:", data.redirect);
            window.location.href = data.redirect; // 결과 페이지로 이동
        } else {
            studentCorrectnessBox.textContent = data.is_correct ? "정답" : "오답";
            aiCorrectnessBox.textContent = data.ai_correct ? "정답" : "오답";
            studentAccuracyBox.textContent = `학생 정답률: ${(data.student_accuracy * 100).toFixed(2)}%`;
            aiAccuracyBox.textContent = `AI 정답률: ${(data.ai_accuracy * 100).toFixed(2)}%`;
             // 응답 시간 업데이트
            const studentResponseTime = document.getElementById("studentResponseTime");
            const aiResponseTime = document.getElementById("aiResponseTime");
            studentResponseTime.textContent = `${data.student_time.toFixed(2)}초`;
            aiResponseTime.textContent = `${data.ai_response_time.toFixed(2)}초`;
            statusText.textContent = data.is_correct ? "정답입니다!" : "오답입니다.";
    
            // 일정 시간 후 다음 문제 로드
            setTimeout(() => {
                loadNextQuestion(); // 다음 문제 비동기 로드
            }, 2000); // 2초 후 이동
        }
    }
    
    
    nextQuestionButton.addEventListener("click", function () {
        const studentCorrectness = studentCorrectnessBox.textContent.trim();
        const warningMessage = document.getElementById("warningMessage");
        // 디버깅: DOM 요소와 값 확인
        console.log("StudentCorrectnessBox element:", studentCorrectnessBox);
        console.log("StudentCorrectnessBox text content:", studentCorrectness);

    
        console.log("Student correctness:", studentCorrectness); // 현재 상태 확인용 로그
    
        // 조건: 문제를 풀지 않았을 경우 경고 메시지 표시
        if (studentCorrectness === "" || studentCorrectness.includes("기다리는 중")) {
            warningMessage.style.display = "block"; // 경고 메시지 표시
            console.warn("Cannot proceed to the next question. The problem is not solved.");
            return; // 다음 문제로 넘어가지 않음
        }
    
        // 경고 메시지 숨기기
        warningMessage.style.display = "none";
        console.log("Next question button clicked.");
        location.reload(); // 페이지 새로고침
    });


    micButton.addEventListener("click", () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    
});
