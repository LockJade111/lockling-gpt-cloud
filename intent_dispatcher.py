import os
from check_permission import (
    check_secret_permission,
    check_register_permission,
    add_register_authorization,
    revoke_authorization,
)

# ✅ 密钥验证
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    persona = intent.get("persona", "").strip()
    secret = intent.get("secret", "").strip()

    if check_secret_permission(persona, secret):
        return {
            "reply": "✅ 密钥验证通过，权限已激活。",
            "intent": intent
        }
    else:
        return {
            "reply": "🚫 密钥错误，身份验证失败。",
            "intent": intent
        }

# ✅ 身份授权：如将军授权司铃注册 persona
def handle_confirm_identity(intent):
    print("📥 收到意图：confirm_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()
    requires = intent.get("requires", "").strip()

    if not (authorizer and grantee and secret and requires):
        return {
            "reply": "⚠️ 授权失败，缺少身份、口令或目标权限。",
            "intent": intent
        }

    if requires == "register_persona" and check_secret_permission(authorizer, secret):
        success = add_register_authorization(authorizer, grantee)
        if success:
            return {
                "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册 persona 权限。",
                "intent": intent
            }
        else:
            return {
                "reply": "⚠️ 授权失败，可能已存在或写入失败。",
                "intent": intent
            }

    return {
        "reply": "🚫 权限不足，拒绝操作。",
        "intent": intent
    }

# ✅ persona 注册
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    registrant = intent.get("persona", "").strip()
    new_name = intent.get("new_name", "").strip()

    # 从 .env 检查是否有被授权
    if check_register_permission(registrant, new_name):
        os.environ[f"PERSONA_{new_name}"] = "active"
        return {
            "reply": f"✅ persona '{new_name}' 注册成功，欢迎加入。",
            "intent": intent
        }
    else:
        return {
            "reply": f"🚫 '{registrant}' 无注册 '{new_name}' 的权限。",
            "intent": intent
        }

# ✅ 撤销授权
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not (authorizer and grantee):
        return {
            "reply": "⚠️ 撤销失败，缺少必要信息。",
            "intent": intent
        }

    success = revoke_authorization(authorizer, grantee)
    if success:
        return {
            "reply": f"✅ 授权已撤销：{authorizer} -> {grantee}",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 撤销失败，未找到对应授权或写入失败。",
            "intent": intent
        }

# ✅ 分发意图
def dispatch_intent(intent):
    try:
        intent_type = intent.get("intent_type", "").strip()
        print(f"🧠 调试中：intent_type={intent_type} | requires={intent.get('requires')} | persona={intent.get('persona')}")

        if intent_type == "confirm_secret":
            return handle_confirm_secret(intent)
        elif intent_type == "confirm_identity":
            return handle_confirm_identity(intent)
        elif intent_type == "register_persona":
            return handle_register_persona(intent)
        elif intent_type == "revoke_identity":
            return handle_revoke_identity(intent)
        else:
            return {
                "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                "intent": intent
            }
    except Exception as e:
        return {
            "reply": f"💥 系统错误：{str(e)}",
            "intent": intent
        }
