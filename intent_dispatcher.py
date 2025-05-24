from check_permission import check_secret_permission
from persona_keys import (
    register_persona,
    check_persona_secret,
    revoke_persona,
    delete_persona,
    unlock_persona
)

# ✅ 密钥验证
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    persona = intent.get("persona", "").strip()
    secret = intent.get("secret", "").strip()

    if check_secret_permission(persona, secret):
        return {
            "status": "success",
            "reply": "✅ 密钥验证通过，身份已确认。",
            "intent": intent
        }
    else:
        return {
            "status": "fail",
            "reply": "🚫 密钥错误，身份验证失败。",
            "intent": intent
        }

# ✅ 注册 persona（支持传入角色）
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    persona = intent.get("persona", "").strip()
    new_name = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()
    role = intent.get("role", "user").strip()

    if not new_name:
        return {
            "status": "fail",
            "reply": "❌ 注册失败：未指定新 persona 名称。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "🚫 身份验证失败，无法注册新 persona。",
            "intent": intent
        }

    register_persona(new_name, secret, created_by=persona, role=role)
    return {
        "status": "success",
        "reply": f"✅ 注册成功：{persona} 成功创建了新角色 {new_name}（角色等级：{role}）",
        "intent": intent
    }

# ✅ 撤销权限（仅将军可执行）
def handle_revoke_identity(intent):
    print("🗑️ 收到意图：revoke_identity")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()

    if persona != "将军":
        return {
            "status": "fail",
            "reply": "🚫 权限不足，只有将军可以撤销授权。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "🚫 身份验证失败，撤销失败。",
            "intent": intent
        }

    revoke_persona(target)
    return {
        "status": "success",
        "reply": f"✅ 授权已撤销：{target} 现在无权再注册新角色。",
        "intent": intent
    }

# ✅ 删除 persona（仅将军可执行）
def handle_delete_persona(intent):
    print("🗑️ 收到意图：delete_persona")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()

    if persona != "将军":
        return {
            "status": "fail",
            "reply": "🚫 权限不足，只有将军可以删除角色。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "🚫 身份验证失败，删除失败。",
            "intent": intent
        }

    delete_persona(target)
    return {
        "status": "success",
        "reply": f"✅ 角色已删除：{target} 已从系统中注销。",
        "intent": intent
    }

# ✅ 解锁 persona（仅将军可执行）
def handle_unlock_persona(intent):
    print("🔓 收到意图：unlock_persona")
    persona = intent.get("persona", "").strip()
    secret = intent.get("secret", "").strip()
    target = intent.get("target", "").strip()

    if persona != "将军":
        return {
            "status": "fail",
            "reply": "🚫 权限不足，只有将军可以解锁账号。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "🚫 身份验证失败，解锁失败。",
            "intent": intent
        }

    success = unlock_persona(target)
    if success:
        return {
            "status": "success",
            "reply": f"✅ 解锁成功：{target} 已恢复访问权限。",
            "intent": intent
        }
    else:
        return {
            "status": "fail",
            "reply": f"❌ 解锁失败：{target} 不存在或数据库异常。",
            "intent": intent
        }

# ✅ 主调度函数
def dispatch_intents(intent):
    intent_type = intent.get("intent_type", "unknown")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    elif intent_type == "delete_persona":
        return handle_delete_persona(intent)
    elif intent_type == "unlock_persona":
        return handle_unlock_persona(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❌ 无法识别意图类型：{intent_type}",
            "intent": intent
        }

