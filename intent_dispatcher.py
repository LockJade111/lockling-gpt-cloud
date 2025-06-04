import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ✅ 自定义模块导入
from generate_reply_with_gpt import handle_chitchat, generate_reply
from library.parse_intent_prompt import get_parse_intent_prompt
from library.lockling_prompt import get_chitchat_prompt_system, format_user_message
from check_permission import (
    check_secret_permission,
    check_persona_secret,
    SUPER_SECRET_KEY
)

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
        # ✅ 新增验证模块调用
        if not check_persona_secret(persona, secret):
            intent["intent_type"] = "unauthorized"
            intent["reason"] = "身份验证失败：密钥错误或未登记。" 

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


# ✅ 身份确认处理模块（确认 requestor + 密钥）
def handle_confirm_identity(intent):
    print("🔍 来自 intent_dispatcher.py 的身份验证开始")
    requestor = intent.get("requestor", "")
    secret = intent.get("secret", "")

    # 超级密钥身份直通
    if requestor == "将军" and secret == SUPER_SECRET_KEY:
        return {
            "status": "success",
            "reply": "✅ 身份已确认，将军口令无误。",
            "intent": intent
        }

    # 数据库验证
    if check_persona_secret(requestor, secret):
        return {
            "status": "success",
            "reply": f"✅ 身份已确认，{requestor} 密钥匹配成功。",
            "intent": intent
        }

    return {
        "status": "fail",
        "reply": f"❌ 身份验证失败，{requestor} 密钥错误或未登记。",
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



def dispatch_intent(intent: dict, persona: str):
    intent_type = intent.get("intent_type", "unknown")
    raw_text = intent.get("raw", "")

    if intent_type == "unauthorized":
        return f"⛔️ 拒绝访问：{intent.get('reason', '无权限')}"

    elif intent_type == "chitchat":
        return handle_chitchat(raw_text, persona)

    elif intent_type == "advice":
        return strategist_advice(raw_text)

    elif intent_type == "view_logs":
        return "🗂 查看日志功能尚在开发中"

    # 可继续添加更多意图分支，如: memory_query, system_status, etc.
    else:
        return f"🤔 暂无法理解你的意图「{intent_type}」"
