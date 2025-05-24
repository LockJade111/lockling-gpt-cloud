from check_permission import check_secret_permission

# ✅ 密钥验证响应
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

# ✅ 注册 persona
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    persona = intent.get("persona", "").strip()
    new_name = intent.get("target", "").strip()

    if not new_name:
        return {
            "status": "fail",
            "reply": "❌ 注册失败：未指定新 persona 名称。",
            "intent": intent
        }

    return {
        "status": "success",
        "reply": f"✅ 注册成功：{persona} 成功创建了新角色 {new_name}。",
        "intent": intent
    }

# ✅ 撤销授权（revoke_identity）
def handle_revoke_identity(intent):
    print("🗑️ 收到意图：revoke_identity")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()

    if not target:
        return {
            "status": "fail",
            "reply": "❌ 撤销失败：未指定目标 persona。",
            "intent": intent
        }

    return {
        "status": "success",
        "reply": f"✅ 授权已撤销：{target} 现在无权再注册新角色。",
        "intent": intent
    }

# ✅ 删除角色（delete_persona）
def handle_delete_persona(intent):
    print("🗑️ 收到意图：delete_persona")
    target = intent.get("target", "").strip()

    if not target:
        return {
            "status": "fail",
            "reply": "❌ 删除失败：未指定要删除的角色。",
            "intent": intent
        }

    return {
        "status": "success",
        "reply": f"✅ 角色已删除：{target} 已从系统中注销。",
        "intent": intent
    }

# ✅ 主调度器
async def dispatch_intent(intent):
    try:
        intent_type = intent.get("intent_type", "unknown")
        print(f"🎯 分发意图类型：{intent_type}")

        if intent_type == "confirm_secret":
            return handle_confirm_secret(intent)

        elif intent_type == "register_persona":
            return handle_register_persona(intent)

        elif intent_type == "revoke_identity":
            return handle_revoke_identity(intent)

        elif intent_type == "delete_persona":
            return handle_delete_persona(intent)

        else:
            return {
                "status": "fail",
                "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                "intent": intent
            }

    except Exception as e:
        return {
            "status": "fail",
            "reply": f"❌ 意图调度失败：{str(e)}",
            "intent": intent
        }
