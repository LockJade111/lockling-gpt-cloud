import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def handle_chitchat(intent: dict) -> dict:
    print("📥 收到意图：chitchat")

    raw = intent.get("raw_message", "").strip()

    prompt = f"""
你是 Lockling，一位亲切、机智的门店守护精灵，负责与客人交流。

当前用户说的话是：
「{raw}」

请用一句自然、有温度的语言进行回复，不要重复用户内容，也不要问“有什么可以帮你”，要有个性地回应。回复只需一句中等长度的话。
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "system", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"🐛 回复生成失败：{str(e)}"

    return {
        "status": "success",
        "reply": reply,
        "intent": intent
    }
