import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    revoke_authorization,
    add_register_authorization,
)
from env_utils import add_authorization_env, activate_persona

# ✅ 密钥验证（模拟将军密钥确认授权过程）
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ 授权流程第一步：提示输入身份
def handle_begin_auth(intent):
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ 授权流程第二步：身份 + 授权写入
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
            "reply": f"⚠️ 授权失败，可能已存在或写入失败。",
            "intent": intent
        }

# ✅ 注册新 persona
def handle_register_persona(intent):
    name = intent.get("new_name", "").strip()
    if not name:
        return {
            "reply": "⚠️ 注册失败，缺少角色名称。",
            "intent": intent
        }

    activate_persona(name)
    return {
        "reply": f"✅ persona 注册成功：{name}",
        "intent": intent
    }

# ✅ 查询权限
def handle_query_permission(intent, persona):
    perms = get_persona_permissions(persona)
    return {
        "reply": f"🔐 当前权限：{perms}",
        "intent": intent
    }

# ✅ 撤销授权
def handle_revoke_authorization(intent, persona):
    target = intent.get("target", "").strip()
    if not target:
        return {
            "reply": "⚠️ 撤销失败，缺少目标。",
            "intent": intent
        }

    success = revoke_authorization(persona, target)
    if success:
        return {
            "reply": f"🔻 授权已撤销：{persona} → {target}",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 撤销失败，记录不存在。",
            "intent": intent
        }

# ✅ 权限同步占位（如需用 Supabase 自动同步）
def handle_sync_permission(intent, persona):
    return {
        "reply": f"🌀 权限同步逻辑尚未启用（开发中）",
        "intent": intent
    }

# ✅ 主调度器：根据 intent_type 调用分支
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "").strip()

    try:
        if intent_type == "confirm_secret":
            return handle_confirm_secret(intent)
        elif intent_type == "begin_auth":
            return handle_begin_auth(intent)
        elif intent_type == "confirm_identity":
            return handle_confirm_identity(intent)
        elif intent_type == "register_persona":
            return handle_register_persona(intent)
        elif intent_type == "query_permission":
            return handle_query_permission(intent, persona)
        elif intent_type == "revoke_authorization":
            return handle_revoke_authorization(intent, persona)
        elif intent_type == "sync_permission":
            return handle_sync_permission(intent, persona)
        else:
            return {
                "reply": f"❌ 未知意图类型：{intent_type}",
                "intent": intent
            }
    except Exception as e:
        return {
            "reply": f"🚨 执行 intent 时发生错误：{str(e)}",
            "intent": intent
        }
