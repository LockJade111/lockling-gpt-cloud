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
            "status": "success",
            "reply": "✅ 密钥验证通过，权限已激活。",
            "intent": intent
        }
    else:
        return {
            "status": "fail",
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
            "status": "fail",
            "reply": "⚠️ 授权失败，缺少身份、口令或目标权限。",
            "intent": intent
        }

    if requires == "register_persona" and check_secret_permission(authorizer, secret):
        success = add_register_authorization(authorizer, grantee)
        if success:
            return {
                "status": "success",
                "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册 persona 权限。",
                "intent": intent
            }
        else:
            return {
                "status": "fail",
                "reply": f"⚠️ 授权失败：系统写入失败或已存在。",
                "intent": intent
            }
    else:
        return {
            "status": "fail",
            "reply": f"🚫 授权失败：密钥错误或目标权限不合法。",
            "intent": intent
        }

# ✅ 注册 persona（需授权者才能执行）
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    persona = intent.get("persona", "").strip()
    new_name = intent.get("target", "").strip()

    if not new_name:
        return {
            "status": "fail",
            "reply": "❌ 注册失败，未指定新 persona 名称。",
            "intent": intent
        }

    if check_register_permission(persona):
        return {
            "status": "success",
            "reply": f"✅ 注册成功：已创建新 persona {new_name}。",
            "intent": intent
        }
    else:
        return {
            "status": "fail",
            "reply": f"🚫 注册失败：{persona} 没有注册新 persona 的权限。",
            "intent": intent
        }

# ✅ 主意图调度器
async def dispatch_intent(intent):
    try:
        intent_type = intent.get("intent_type", "unknown")
        print(f"🎯 分发意图类型：{intent_type}")

        if intent_type == "confirm_secret":
            return handle_confirm_secret(intent)

        elif intent_type == "confirm_identity":
            return handle_confirm_identity(intent)

        elif intent_type == "register_persona":
            return handle_register_persona(intent)

        else:
            return {
                "status": "fail",
                "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                "intent": intent
            }

    except Exception as e:
        return {
            "status": "error",
            "reply": f"💥 dispatcher 错误：{str(e)}",
            "intent": intent
        }
