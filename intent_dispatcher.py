import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from generate_reply_with_gpt import handle_chitchat
from generate_reply_with_gpt import generate_reply

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 解析意图
def parse_intent(message: str, persona: str, secret: str = ""):
    prompt = f"""
你是云脑中枢系统的语义分析核心模块你不具备人格情绪或形象只负责将用户输入转换为标准结构化 JSON 指令

你的任务是从用户自然语言中提取以下字段
- intent_type意图类型（从预设选项中选一）
- target目标对象（如角色名对象名）
- permissions权限列表（如 读写执行）
- secret密钥字符串（如用户验证口令）

规则说明
1. 你不做任何解释不回复用户不闲聊；
2. 若意图模糊不清则 intent_type 为 "unknown"；
3. 对于 intent_type 为 "chitchat" 的情况target 和 secret 应留空；
4. 输出必须是**合法 JSON**不能有多余解释

可选 intent_type
- confirm_secret
- register_persona
- confirm_identity
- revoke_identity
- delete_persona
- authorize
- update_secret
- chitchat
- unknown

请解析以下用户输入
{message}
"""

""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        content = response.choices[0].message.content.strip()

        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_str = content[json_start:json_end]

        intent = json.loads(json_str)

        # ✅ 补充字段
        intent["persona"] = persona
        intent["secret"] = secret

        # ✅ 严格清理非目标字段
        for key in list(intent.keys()):
            if key not in ["intent_type", "target", "permissions", "secret", "persona", "raw_message"]:
                intent.pop(key)

        return intent

    except Exception as e:
        return {
            "intent_type": "unknown",
            "persona": persona,
            "secret": secret,
            "target": "",
            "permissions": [],
            "reason": f"GPT解析异常{str(e)}",
            "raw": content if 'content' in locals() else "无返回"
        }

# ✅ 闲聊意图处理模块（GPT生成自然语言回复）
def handle_chitchat(intent):
    print("📥 收到意图chitchat")
    raw = intent.get("raw_message", "").strip()

    prompt = f"""
你是 Lockling, 一位智慧又可靠的门店守护精灵。客人刚刚说：
{raw}

请你用一句自然、有亲和力、不重复用户内容的中文回答。不要说“我在”或“有什么可以帮你”，而是直接接话或回应，控制在20字以内。
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()
        print("🎯 GPT 回复内容", reply)
    except Exception as e:
        reply = f"🐛 回复失败{str(e)}"

    return {
        "status": "success",
        "reply": reply,
        "intent": intent
    }

# ✅ 主控分发器（根据 intent_type 分发到不同处理函数）
def intent_dispatcher(intent):
    intent_type = intent.get("intent_type", "")

    if intent_type == "chitchat":
        return handle_register(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "update_secret":
        return handle_update_secret(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    elif intent_type == "delete_persona":
        return handle_delete_persona(intent)
    elif intent_type == "chitchat":
        return handle_chitchat(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的指令类型: {intent_type}",
            "intent": intent
        }

# 供外部模块 import 使用
__all__ = ["intent_dispatcher"]
