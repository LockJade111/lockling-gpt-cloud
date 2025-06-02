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

    const wrapper = document.createElement("div");
    wrapper.className = "bot-message-with-avatar";

    const bubble = document.createElement("div");
    bubble.className = "bot-bubble";
    bubble.textContent = "⌛ typing...";

    wrapper.appendChild(bubble);
    msg.appendChild(wrapper);

  } else if (type === "bot") {
    const wrapper = document.createElement("div");
    wrapper.className = "bot-message-with-avatar";

    const avatar = document.createElement("img");
    avatar.src = "/static/img/lockling-avatar.png";
    avatar.className = "avatar";

    const bubble = document.createElement("div");
    bubble.className = "bot-bubble";
    bubble.innerHTML = text;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    msg.appendChild(wrapper);

  } else {
    // ✅ 正确渲染 user 消息，无嵌套气泡
    const bubble = document.createElement("div");
    bubble.className = "user-bubble";
    bubble.innerHTML = `<strong>${sender}:</strong> ${text}`;
    msg.appendChild(bubble);
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
