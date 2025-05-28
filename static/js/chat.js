document.getElementById("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    // 🧱 正确获取输入框
    const input = document.getElementById("user-input");
    if (!input) {
        console.error("❌ 找不到 input 输入框（id=user-input）");
        return;
    }

    const message = input.value.trim();
    if (!message) return;

    appendMessage("你", message, "user");

    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                persona: "将军",       // ✅ 可改为动态绑定
                secret: "玉衡在手"     // ✅ 后续可接 UI 设置
            }),
        });

        const data = await response.json();

        // ✅ 智能判断回复格式并转换为字符串
        let replyText = "";
        if (data?.result?.reply) {
            replyText = data.result.reply;
        } else if (data?.reply) {
            replyText = data.reply;
        } else {
            replyText = typeof data === "string" ? data : JSON.stringify(data, null, 2);
        }

        appendMessage("锁灵", replyText, "bot");

    } catch (error) {
        appendMessage("锁灵", `❌ 网络错误：${error}`, "bot");
    }
});

function appendMessage(sender, text, cls) {
    const chatBox = document.getElementById("chat-box");
    if (!chatBox) {
        console.error("❌ chat-box 容器不存在");
        return;
    }

    const msg = document.createElement("div");
    msg.className = `message ${cls}-message`;

    // ✅ 判断输出内容类型并美化
    if (typeof text === "object") {
        try {
            msg.textContent = `${sender}： ${text?.reply || "[无回应]"}`;
        } catch (err) {
            msg.textContent = `${sender}： [无法解析对象]`;
        }
    } else {
        msg.textContent = `${sender}： ${text}`;
    }

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}
