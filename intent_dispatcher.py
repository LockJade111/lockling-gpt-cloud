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

# ✅ 授权身份
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
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册 persona 权限。",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 授权失败，可能已存在或写入失败。",
            "intent": intent
        }

# ✅ 注册 persona
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    operator = intent.get("persona", "").strip()
    new_name = intent.get("new_name", "").strip()

    # 权限校验
    if not check_permission(operator, "register_persona"):
        return {
            "reply": "🚫 权限不足，拒绝注册操作。",
            "intent": intent
        }

    # 更新 .env
    env_path = ".env"
    env_line = f"PERSONA_{new_name} = active\n"
    try:
        with open(env_path, "a") as f:
            f.write(env_line)
        print(f"✅ persona 注册成功：{new_name}")
        return {
            "reply": f"✅ persona '{new_name}' 注册成功，欢迎加入。",
            "intent": intent
        }
    except Exception as e:
        print(f"❌ persona 注册失败: {e}")
        return {
            "reply": f"❌ 注册失败，系统错误：{str(e)}",
            "intent": intent
        }

# ✅ 撤销授权
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    authorizer = intent.get("identity", "").strip()
    target = intent.get("target", "").strip()

    if not authorizer or not target:
        return {
            "reply": "⚠️ 撤销失败，缺少身份或目标。",
            "intent": intent
        }

    success = revoke_authorization(authorizer, target)
    if success:
        return {
            "reply": f"✅ 已成功取消 {target} 的注册权限授权。",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 撤销失败，可能目标未被授权或数据异常。",
            "intent": intent
        }

# ✅ 统一调度入口
def dispatch_intent(intent_type, intent_data, persona):
    print(f"🧠 调试中: intent_type={intent_type} | requires={intent_data.get('requires', '')} | persona={persona}")
    
    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent_data)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent_data)
    elif intent_type == "register_persona":
        return handle_register_persona(intent_data)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent_data)
    else:
        return {
            "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
            "intent": intent_data,
            "persona": persona
        }
