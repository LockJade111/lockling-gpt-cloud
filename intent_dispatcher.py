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
from prompt_library.parse_intent_prompt import get_parse_intent_prompt
...
prompt = get_parse_intent_prompt(message)

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

from prompt_library.lockling_prompt import get_chitchat_prompt_system, format_user_message

# ✅ 闲聊意图处理模块（GPT生成自然语言回复）
def handle_chitchat(intent):
    print("📥 收到意图 chitchat")
    raw = intent.get("raw", "")

    try:
        prompt = get_chitchat_prompt_system()
        user_msg = format_user_message(raw)

        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt},
                user_msg
            ]
        )
        reply = response.choices[0].message.content.strip()
        print("🎯 GPT 回复内容", reply)
    except Exception as e:
        reply = f"🐛 回复失败：{str(e)}"

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
