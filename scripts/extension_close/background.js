const ENDPOINT = "http://127.0.0.1:8001/main/close_browser/";

chrome.windows.onRemoved.addListener((windowId) => {
  // اینجا دقیقاً وقتی کاربر روی × پنجره کلیک می‌کنه اجرا می‌شه
  fetch(ENDPOINT, {
    method: "POST",
    // با همین تنظیمات، بادیِ خالی میره و request شما به متد POST view می‌خوره
    credentials: "include"  
  }).catch(err => {
    console.error("Failed to notify server on window close:", err);
  });
});