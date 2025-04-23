const ENDPOINT = "http://127.0.0.1:8000/main/close_browser/";

// Listen for WINDOW CLOSURE (user clicks X)
chrome.windows.onRemoved.addListener((windowId) => {
  fetch(ENDPOINT, { method: "GET" })
    .catch(err => console.error("Window close request failed:", err));
});
