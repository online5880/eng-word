// 인증된 사용자만 로그아웃 로그 요청 전송
window.addEventListener("beforeunload", function () {
    if (isUserAuthenticated()) {
        navigator.sendBeacon('/api/logout-log/'); // 로그아웃 로그 기록
    }
});

// Django에서 인증 상태 확인
function isUserAuthenticated() {
    return document.body.getAttribute("data-authenticated") === "true";
}