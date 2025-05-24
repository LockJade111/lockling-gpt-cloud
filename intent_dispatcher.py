import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ intent: confirm_secret
def handle_confirm_secret(intent):
    print("📥 调用：handle_confirm_secret")
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent: begin_auth
def handle_begin_auth(intent):
    print("📥 调用：handle_begin_auth")
    target = intent.get("target", "未知对象")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ intent: confirm_identity
def handle_confirm_identity(intent):
    print("📥 调用：handle_confirm_identity")
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

# ✅ intent: register_persona
def handle_register_persona(intent):
    print("📥 调用：handle_register_persona")
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

# ✅ dispatch_intents 主调度函数
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "").strip()
    print(f"🐛 调试：dispatch_intents 接收到 intent_type={intent_type} | persona={persona}")

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
            "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
            "intent": intent
        }
