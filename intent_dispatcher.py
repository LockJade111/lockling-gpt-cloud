from check_permission import check_persona_secret
from persona_keys import register_persona
from supabase_logger import write_log_to_supabase

# ✅ 注册 persona intent
def handle_register(intent):
    print("📥 收到意图：register")

    persona = intent.get("persona", "").strip()
    new_name = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()

    if not persona or not new_name or not secret:
        return {
            "status": "fail",
            "reply": "❗ 缺少 persona、target 或 secret 字段。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "❌ 注册失败：操作者密钥错误。",
            "intent": intent
        }

    try:
        result = register_persona(new_name, secret)
        write_log_to_supabase(persona, intent, "success", f"注册新 persona：{new_name}")
        return {
            "status": "success",
            "reply": f"✅ 已注册新角色：{new_name}",
            "intent": intent
        }
    except Exception as e:
        write_log_to_supabase(persona, intent, "fail", str(e))
        return {
            "status": "fail",
            "reply": f"❌ 注册失败：{str(e)}",
            "intent": intent
        }

# ✅ 授权权限 intent（示例占位）
def handle_authorize(intent):
    print("📥 收到意图：authorize")
    return {
        "status": "success",
        "reply": "（模拟授权成功）",
        "intent": intent
    }

# ✅ 主分发器
def dispatch(intent):
    intent_type = intent.get("intent_type", "")
    if intent_type == "register":
        return handle_register(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的意图类型：{intent_type}",
            "intent": intent
        }
