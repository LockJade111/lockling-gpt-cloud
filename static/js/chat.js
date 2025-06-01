// chat.js — Lockling 官网嵌入版（重构完成版）
document.addEventListener("DOMContentLoaded", () => {
  initChatForm();
});

function initChatForm() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  if (!form || !input || !chatBox) {
    console.error("❌ 聊天窗口初始化失败，检查表单或输入框是否存在。");
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    appendMessage("你", message, "user");
    input.value = "";

    // 添加“锁灵正在思考中...”的临时消息
    appendMessage("锁灵", "⌛ 正在思考中...", "bot-temp");

    await sendMessage(message);
  });
}

async function sendMessage(message) {
  const tempMsg = document.querySelector(".bot-temp-message");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        persona: "锁灵",       // ✅ 后续可用 localStorage / 用户设置 替换
        secret: "玉衡在手"     // ✅ 安全建议：勿在生产环境硬编码密钥
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

    // 移除“正在思考中”临时消息
    if (tempMsg) tempMsg.remove();

    appendMessage("锁灵", replyText, "bot");

  } catch (error) {
    if (tempMsg) tempMsg.remove();
    appendMessage("锁灵", `❌ 网络错误：${error.message || error}`, "bot");
  }
}

function appendMessage(sender, text, type) {
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;

  const msg = document.createElement("div");
  msg.className = `message ${type}-message`;

  if (type === "bot-temp") {
    msg.classList.add("bot-temp-message"); // 临时消息，用于替换
  }

  // 判断类型美化
  if (typeof text === "object") {
    try {
      msg.textContent = `${sender}：${text?.reply || "[无回应]"}`;
    } catch (err) {
      msg.textContent = `${sender}：[无法解析内容]`;
    }
  } else {
    msg.textContent = `${sender}：${text}`;
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

