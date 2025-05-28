document.getElementById("chat-form").addEventListener("submit", async function(e) {
    e.preventDefault();

    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage("你", message, "user");
    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message: message
        })
    });

    const data = await response.json();
    appendMessage("锁灵", data.reply || "[无回复]", "bot");
});

function appendMessage(sender, text, cls) {
    const msgBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.classList.add("message", cls);
    div.innerHTML = `<span class="${cls}">${sender}：</span> ${text}`;
    msgBox.appendChild(div);
    msgBox.scrollTop = msgBox.scrollHeight;
}
