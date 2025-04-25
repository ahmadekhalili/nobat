chrome.windows.onBoundsChanged.addListener(async (window) => {
  try {
    const win = await chrome.windows.get(window.id);

    if (win.state === "minimized") {
      const url = `http://127.0.0.1:8000/main/browser_minimize?windowId=${win.id}&state=minimized`;

      await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
  } catch (err) {
    console.error("Failed to send minimize request:", err);
  }
});
