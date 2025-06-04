document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-button");

  function appendToChat(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendToChat("你", message);
    input.value = "";

    try {
      const res = await fetch("/advisor/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          secret: "your_dev_key" // ⛳️ 替换成你的实际密钥
        }),
      });

      const data = await res.json();
      appendToChat("军师", data.response || data.error || "⚠️ 无回复");
    } catch (err) {
      appendToChat("系统", "❌ 请求失败，请检查网络或后端服务。");
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});
