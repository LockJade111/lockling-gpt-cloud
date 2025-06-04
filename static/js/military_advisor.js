async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  appendToChat("你", message);
  input.value = "";

  const res = await fetch("/advisor/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  appendToChat("军师", data.response);
}

function appendToChat(sender, text) {
  const chatBox = document.getElementById("chat-box");
  const messageDiv = document.createElement("div");
  messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendToAdvisor() {
    const message = document.getElementById("userInput").value;

    fetch("/advisor/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, secret: "your_dev_key" })  // ⛳️ 替换成真实密钥
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("responseArea").innerText = data.response || data.error;
    });
}
