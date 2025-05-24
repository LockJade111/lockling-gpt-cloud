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

# ✅ intent 处理：执行注册授权
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
            "reply": f"⚠️ 授权失败，操作未生效。",
            "intent": intent
        }

# ✅ intent 处理：取消授权
def handle_revoke_identity(intent):
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 取消失败，缺少身份或目标。",
            "intent": intent
        }

    success = revoke_authorization(authorizer, grantee)
    if success:
        return {
            "reply": f"✅ 已取消授权：{authorizer} 不再授权 {grantee}。",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 取消失败，可能不存在该授权关系。",
            "intent": intent
        }

# ✅ intent 处理：注册新角色
def handle_register_persona(intent):
    new_name = intent.get("new_name", "").strip()
    if not new_name:
        return {
            "reply": "⚠️ 注册失败，缺少角色名。",
            "intent": intent
        }
    activate_persona(new_name)
    return {
        "reply": f"✅ 新 persona 已注册并激活：{new_name}",
        "intent": intent
    }

# ✅ 主调度函数
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
        return handle_register_persona(intent)
    else:
        return {
            "reply": f"❌ 未知意图类型：{intent_type}",
            "intent": intent
        }
