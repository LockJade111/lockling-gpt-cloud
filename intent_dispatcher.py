import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    add_register_authorization,
    revoke_authorization,
)
from env_utils import add_authorization_env, activate_persona

# ✅ intent 处理：密钥确认
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent 处理：开始身份确认
def handle_begin_auth(intent):
    print("📥 收到意图：begin_auth")
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ intent 处理：确认身份 → 注册授权
def handle_confirm_identity(intent):
    print("📥 收到意图：confirm_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 授权失败，缺少身份或目标。",
            "intent": intent
        }

    success = add_register_authorization(authorizer, grantee)
    if success:
        add_authorization_env(authorizer, grantee)
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册 persona 权限。",
            "intent": intent
        }
    else:
        return {
            "reply": "⚠️ 授权失败，写入失败。",
            "intent": intent
        }

# ✅ intent 处理：撤销身份授权
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 撤销失败，缺少身份或目标。",
            "intent": intent
        }

    success = revoke_authorization(authorizer, grantee)
    if success:
        return {
            "reply": f"✅ 授权已取消：{authorizer} 撤销 {grantee} 的注册权限。",
            "intent": intent
        }
    else:
        return {
            "reply": "⚠️ 撤销失败，未能从列表移除。",
            "intent": intent
        }

# ✅ intent 处理：注册新 persona 并激活
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    new_name = intent.get("new_name", "").strip()

    if not new_name:
        return {
            "reply": "⚠️ 注册失败，缺少 persona 名称。",
            "intent": intent
        }

    activate_persona(new_name)
    return {
        "reply": f"✅ persona '{new_name}' 注册成功，欢迎加入。",
        "intent": intent
    }

# ✅ 主调度器：根据 intent_type 分发
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "unknown")
    print(f"🧭 调试中: intent_type={intent_type} | persona={persona}")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    else:
        print("❌ dispatch_intents 无法识别意图类型")
        return {
            "reply": f"❌ 未知意图类型：{intent_type}",
            "intent": {
                "intent": "unknown",
                "intent_type": "unknown",
                "source": intent.get("source", "")
            },
            "persona": persona
        }
