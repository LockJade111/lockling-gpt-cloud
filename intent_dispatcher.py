import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ✅ 自定义模块导入
from generate_reply_with_gpt import handle_chitchat, generate_reply
from library.parse_intent_prompt import get_parse_intent_prompt
from library.lockling_prompt import get_chitchat_prompt_system, format_user_message
from check_permission import check_secret_permission

# ✅ 加载 API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 意图解析函数
def parse_intent(message: str, persona: str, secret: str = ""):
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
        intent["raw"] = message

        # ✅ 严格清理字段
        for key in list(intent.keys()):
            if key not in ["intent_type", "target", "permissions", "secret", "persona", "raw"]:
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

# ✅ 闲聊意图处理
def handle_chitchat(intent):
    print("📥 收到意图 chitchat")

    if intent.get("intent_type") != "chitchat":
        return {"status": "error", "reason": "⚠️ 非 chitchat 意图不应进此函数"}

    raw = intent.get("raw", "")
    persona = intent.get("persona", "")
    secret = intent.get("secret", "")

    check_result = check_secret_permission(intent, persona, secret)
    if not check_result["allow"]:
        print("🚫 权限拒绝：", check_result["reason"])
        return {
            "status": "unauthorized",
            "reply": check_result["reason"],
            "intent": intent
        }

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
        print("🎯 GPT 回复内容:", reply)

        return {
            "status": "success",
            "reply": reply,
            "intent": intent
        }

    except Exception as e:
        print("❌ GPT 回复出错：", e)
        return {
            "status": "error",
            "reason": str(e),
            "intent": intent
        }

# ✅ 主控分发器
def intent_dispatcher(intent):
    intent_type = intent.get("intent_type", "")

    if intent_type == "authorize":
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
    elif intent_type == "register":
        return handle_register(intent)
    elif intent_type == "chitchat":
        return handle_chitchat(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的指令类型: {intent_type}",
            "intent": intent
        }

# ✅ 供外部调用
__all__ = ["intent_dispatcher"]
