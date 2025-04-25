// background.js

// Listener is registered at the top level, so Chrome knows to wake the
// service worker when this event occurs.
chrome.windows.onRemoved.addListener((windowId) => {
  console.log(`Window ${windowId} closed. Attempting to connect to native host.`);

  try {
    // Connect to the native host *inside* the event handler
    let port = chrome.runtime.connectNative('com.nobat.browser');

    // Optional: Listen for disconnection or errors on this specific port
    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        console.error(`Native port disconnected with error: ${chrome.runtime.lastError.message}`);
      } else {
        console.log("Native port disconnected normally.");
      }
    });

    // Send the message
    port.postMessage({ event: "window_closed", windowId });
    console.log(`Message sent for window ${windowId}`);

    // Optional but good practice for short-lived connections:
    // Disconnect after sending if you don't need to listen for replies.
    // The native host process usually exits when the port disconnects.
    // port.disconnect(); // Uncomment if you only need to send, not receive

  } catch (error) {
    console.error("Error connecting or sending message to native host:", error);
    // Check chrome.runtime.lastError as connectNative might set it instead of throwing
    if (chrome.runtime.lastError) {
        console.error(`chrome.runtime.lastError: ${chrome.runtime.lastError.message}`);
    }
  }
});

// Optional: Add a listener for messages *from* the native host, if needed.
// This would require keeping the port open (don't call disconnect immediately).

chrome.runtime.onConnectNative.addListener((port) => {
  if (port.name === 'com.nobat.browser') { // Check if it's the expected host
    port.onMessage.addListener((msg) => {
      console.log("Received message from native host:", msg);
    });
    port.onDisconnect.addListener(() => {
       if (chrome.runtime.lastError) {
        console.error(`Native port disconnected with error: ${chrome.runtime.lastError.message}`);
      } else {
        console.log("Native port disconnected.");
      }
    });
  }
});


console.log("Browser Monitor service worker started.");