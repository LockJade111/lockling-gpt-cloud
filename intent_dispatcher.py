import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    revoke_authorization,
    sync_permission,
    add_register_authorization,
    register_new_persona
)
from env_utils import add_authorization_env, activate_persona

# ✅ intent: 密钥验证阶段
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent: 授权流程起始
def handle_begin_auth(intent):
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ intent: 授权执行确认
def handle_confirm_identity(intent):
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 授权失败，缺少授权者或目标。",
            "intent": intent
        }

    success = add_register_authorization(authorizer, grantee, permission="register_persona")
    if success:
        add_authorization_env(authorizer, grantee)
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册新角色权限。",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 授权失败，可能已存在或写入错误。",
            "intent": intent
        }

# ✅ intent: 注册新角色
def handle_register_persona(intent):
    name = intent.get("new_name", "").strip()
    if not name:
        return {
            "reply": "⚠️ 注册失败，缺少新角色名称。",
            "intent": intent
        }

    success = register_new_persona(name)
    if success:
        activate_persona(name)
        return {
            "reply": f"✅ 新 persona 已注册成功：{name}",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ persona {name} 已存在，注册跳过。",
            "intent": intent
        }

# ✅ intent: 查询当前权限
def handle_query_permission(intent, persona):
    perms = get_persona_permissions(persona)
    return {
        "reply": f"🔍 当前权限列表：{perms}",
        "intent": intent
    }

# ✅ intent: 撤销授权
def handle_revoke_authorization(intent, persona):
    target = intent.get("target", "").strip()
    if not target:
        return {
            "reply": "⚠️ 撤销失败，缺少目标对象。",
            "intent": intent
        }

    revoke_authorization(persona, target, permission="register_persona")
    return {
        "reply": f"🔻 授权已撤销：{persona} → {target}",
        "intent": intent
    }

# ✅ intent: 权限同步（从 .env 重建内存）
def handle_sync_permission(intent, persona):
    updated = sync_permission()
    return {
        "reply": f"🔁 权限同步完成，共计更新：{updated} 项",
        "intent": intent
    }

# ✅ 主调度分发器
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type")
    print(f"🧭 dispatch_intents: intent_type={intent_type} | persona={persona}")

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
                "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                "intent": intent
            }
    except Exception as e:
        return {
            "reply": f"❌ dispatch_intents() 执行失败：{str(e)}",
            "intent": {"intent": "unknown", "intent_type": "unknown"}
        }
