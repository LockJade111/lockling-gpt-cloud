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
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent 处理：开始身份确认阶段
def handle_begin_auth(intent):
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ intent 处理：执行注册授权（confirm_identity）
def handle_confirm_identity(intent):
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
            "reply": "❌ 授权失败，系统写入异常。",
            "intent": intent
        }

# ✅ intent 处理：撤销授权（revoke_identity）
def handle_revoke_identity(intent):
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
            "reply": f"✅ 已撤销 {grantee} 的注册权限（由 {authorizer} 授权）。",
            "intent": intent
        }
    else:
        return {
            "reply": "❌ 撤销失败，未找到有效授权关系。",
            "intent": intent
        }

# ✅ intent 处理：注册新 persona（register_persona）
def register_new_persona(intent):
    new_name = intent.get("new_name", "").strip()
    source = intent.get("source", "").strip()

    if not new_name:
        return {
            "reply": "⚠️ 注册失败，缺少角色名称。",
            "intent": intent
        }

    activate_persona(new_name)  # 启动 .env 中的 persona
    return {
        "reply": f"✅ 新 persona {new_name} 已激活，欢迎加入 Lockling 系统。",
        "intent": intent
    }

# ✅ 主调度函数：根据 intent_type 分发处理
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "unknown")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    elif intent_type == "register_persona":
        return register_new_persona(intent)
    else:
        return {
            "reply": f"❌ 未知意图类型：{intent_type}",
            "intent": intent
        }
