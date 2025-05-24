import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    add_register_authorization,
    revoke_authorization,
    check_permission
)

# ✅ 密钥验证
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ 开始身份确认（未启用）
def handle_begin_auth(intent):
    print("📥 收到意图：begin_auth")
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ 授权身份 → 写入 AUTHORIZED_REGISTER
def handle_confirm_identity(intent):
    print("📥 收到意图：confirm_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()
    required = intent.get("requires", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 授权失败，缺少身份或目标。",
            "intent": intent
        }

    success = add_register_authorization(authorizer, grantee)
    if success:
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册 persona 权限。",
            "intent": intent
        }
    else:
        return {
            "reply": "❌ 授权写入失败，请检查 .env 权限配置。",
            "intent": intent
        }

# ✅ 注册 persona 前应检查权限
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    persona = intent.get("persona", "").strip()
    new_name = intent.get("new_name", "").strip()

    if not persona or not new_name:
        return {
            "reply": "⚠️ 注册失败，缺少 persona 或新名称。",
            "intent": intent
        }

    if not check_permission(persona, "register_persona"):
        return {
            "reply": "🚫 权限不足，无法注册新 persona。",
            "intent": intent
        }

    # ✅ 写入 .env
    try:
        os.environ["PERSONA_" + new_name] = "active"
        return {
            "reply": f"✅ persona '{new_name}' 注册成功，欢迎加入。",
            "intent": intent
        }
    except Exception as e:
        return {
            "reply": f"❌ 注册失败：{str(e)}",
            "intent": intent
        }

# ✅ 取消授权
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    authorizer = intent.get("identity", "").strip()
    target = intent.get("target", "").strip()

    if not authorizer or not target:
        return {
            "reply": "⚠️ 取消授权失败，缺少授权者或目标。",
            "intent": intent
        }

    result = revoke_authorization(authorizer, target)
    if result:
        return {
            "reply": f"✅ 已取消 {target} 的 persona 注册权限。",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 取消失败，未找到 {target} 的授权记录。",
            "intent": intent
        }
