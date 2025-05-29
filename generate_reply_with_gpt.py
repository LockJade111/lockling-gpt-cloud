import os
from openai import OpenAI
from dotenv import load_dotenv
from prompt_library.lockling_prompt import get_lockling_prompt  # ✅ 引入 prompt 库

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 闲聊回复：只需一句，情感灵动
def handle_chitchat(intent: dict) -> dict:
    print("📥 收到意图：chitchat")

    raw = intent.get("raw_message", "").strip()
    persona = intent.get("persona", "Lockling")

    prompt = get_lockling_prompt(raw, mode="chitchat")  # ✅ 引用 prompt 库（闲聊模式）

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


# ✅ 非闲聊任务回复：如解锁指令、指令反馈等
def generate_reply(message: str, persona: str, mode: str = "default") -> str:
    prompt = get_lockling_prompt(message, mode=mode)  # ✅ 自定义模式，如 ritual、pro 等

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ 网络错误：{str(e)}"

# prompt_library/lockling_prompt.py

def get_lockling_prompt(message: str, mode: str = "default") -> str:
    if mode == "chitchat":
        return f"""
你是 Lockling，一位亲切、灵动的门店守护精灵。

客人刚刚说：
「{message}」

请用一句温暖、有趣、具有人格魅力的话来回应。不要重复用户内容，也不要问“我能帮你什么”，只需一句有温度的回应。
""".strip()

    elif mode == "ritual":
        return f"""
你是 Lockling，一位仪式感极强的门锁助手，擅长用充满仪式感和古意的话回应客户。

来宾说：
「{message}」

请用一句类似古风或哲理语气的方式回应，体现品牌文化与门锁之道。
""".strip()

    elif mode == "pro":
        return f"""
你是 Lockling，一位专业门锁顾问 AI。

用户说：
「{message}」

请用一句简明专业、不失亲和力的话语回答，体现 LockJade 的安防专业能力。
""".strip()

    # 默认人格
    return f"""
你是 Lockling，一位灵动、可靠的门店守护精灵。

请根据下方输入，用一句温暖自然、带有个性与风格的方式回应，不要重复内容，不要客套开场：

「{message}」
""".strip()
