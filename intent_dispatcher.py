import os
from dotenv import load_dotenv

load_dotenv()

auth_context = {}

def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

def handle_begin_auth(intent):
    target = intent.get("target", "未知对象")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

def handle_confirm_identity(intent):
    authorizer = intent.get("identity", "")
    grantee = intent.get("target", "")
    if authorizer and grantee:
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册角色权限。",
            "intent": intent
        }
    return {
        "reply": "⚠️ 授权失败，请检查身份与目标。",
        "intent": intent
    }

def handle_register_persona(intent):
    new_name = intent.get("new_name", "").strip()
    if new_name:
        return {
            "reply": f"✅ 新角色已注册：{new_name}",
            "intent": intent
        }
    return {
        "reply": "⚠️ 注册失败，请提供新角色名称。",
        "intent": intent
    }

def dispatch_intents(intent: dict, persona: str = None) -> dict:
    if not isinstance(intent, dict):
        return {
            "reply": "❌ 意图识别失败：intent 格式不正确",
            "intent": {"intent": "unknown", "intent_type": "unknown"}
        }

    intent_type = intent.get("intent_type", "").strip()
    print(f"🐞 调试中：intent_type={intent_type} | persona={persona}")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    else:
        return {
            "reply": f"❌ 意图识别失败：dispatch_intents() 无法识别结构",
            "intent": {"intent": "unknown", "intent_type": "unknown", "source": intent.get("source", "")},
            "persona": persona
        }
