// chat.js — Lockling Chat Widget (Enhanced Version)
document.addEventListener("DOMContentLoaded", () => {
  initChatForm();

  // 👋 Welcome message when chat loads
  appendMessage("Lockling", "👋 Welcome to LockJade. Lockling is at your service!", "bot");
});

function initChatForm() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  if (!form || !input || !chatBox) {
    console.error("❌ Chat window initialization failed.");
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    document.getElementById('thinking-indicator').style.display = 'block';

    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message, "user");
    input.value = "";

    // Temporary bot thinking message
    appendMessage("Lockling", "⌛ Lockling is thinking...", "bot-temp");

    await sendMessage(message);
  });
}

async function sendMessage(message) {
  const tempMsg = document.querySelector(".bot-temp-message");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        persona: "Lockling",
        secret: "玉衡在手"
      }),
    });

    const data = await response.json();

    let replyText = "";
    if (data?.result?.reply) {
      replyText = data.result.reply;
    } else if (data?.reply) {
      replyText = data.reply;
    } else {
      replyText = typeof data === "string" ? data : JSON.stringify(data, null, 2);
    }

    if (tempMsg) tempMsg.remove();
    document.getElementById("thinking-indicator").style.display = "none";

    appendMessage("Lockling", replyText, "bot");

  } catch (error) {
    if (tempMsg) tempMsg.remove();
    document.getElementById("thinking-indicator").style.display = "none";
    appendMessage("Lockling", `❌ Network Error: ${error.message || error}`, "bot");
  }
}

function appendMessage(sender, text, type) {
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;

  const msg = document.createElement("div");
  msg.className = `message ${type}-message`;

  if (type === "bot-temp") {
    msg.classList.add("bot-temp-message");
    msg.innerHTML = `
      <div class="bot-message-with-avatar">
        <img src="/static/img/lockling-avatar.png" class="avatar" />
        <div class="bot-bubble">⌛ Lockling is thinking...</div>
      </div>`;
  } else if (type === "bot") {
    msg.innerHTML = `
      <div class="bot-message-with-avatar">
        <img src="/static/img/lockling-avatar.png" class="avatar" />
        <div class="bot-bubble">${text}</div>
      </div>`;
  } else {
    msg.innerHTML = `<div class="user-bubble"><strong>${sender}:</strong> ${text}</div>`;
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
