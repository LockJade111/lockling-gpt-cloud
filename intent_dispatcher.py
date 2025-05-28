import os
from check_permission import check_secret_permission, check_persona_secret, update_persona_secret
from persona_keys import register_persona
from src.supabase_logger import write_log_to_supabase
from supabase import create_client
from secret_manager import verify_secret, generate_new_secret

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 注册 persona intent
def handle_register(intent):
    print("📥 收到意图：register_persona")

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
        write_log_to_supabase(
            query=persona,
            reply=f"注册新 persona：{new_name}",
            intent_result=intent,
            status="success"
        )
        new_secret = generate_new_secret()
        return {
            "status": "success",
            "reply": f"✅ 已注册新角色：{new_name}\n🆕 新口令已生成：{new_secret}",
            "intent": intent
        }
    except Exception as e:
        write_log_to_supabase(
            query=persona,
            reply=str(e),
            intent_result=intent,
            status="fail"
        )
        return {
            "status": "fail",
            "reply": f"❌ 注册失败：{str(e)}",
            "intent": intent
        }

# ✅ 更新密钥 intent
def handle_update_secret(intent):
    print("🔐 收到意图：update_secret")

    persona = intent.get("persona", "").strip()
    old_secret = intent.get("secret", "").strip()
    new_secret = intent.get("target", "").strip()

    if not persona or not old_secret or not new_secret:
        return {
            "status": "fail",
            "reply": "❌ 更新失败：缺少必要信息。",
            "intent": intent
        }

    if not check_persona_secret(persona, old_secret):
        return {
            "status": "fail",
            "reply": "❌ 密钥更新失败：原密钥验证不通过。",
            "intent": intent
        }

    update_persona_secret(persona, new_secret)

    return {
        "status": "success",
        "reply": f"🔑 密钥已成功更新为：「{new_secret}」",
        "intent": intent
    }

# ✅ 身份验证 intent
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    return {
        "status": "success",
        "reply": f"✅ 密钥已确认",
        "intent": intent
    }

# ✅ 闲聊意图
def handle_chitchat(intent):
    print("📥 收到意图：chitchat")
    return {
        "status": "success",
        "reply": "🗣️ 我在呢，有什么我可以帮你的吗？",
        "intent": intent
    }

# ✅ 撤销授权 intent（占位）
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    return {
        "status": "success",
        "reply": f"⚠️ 尚未实现撤销授权功能，占位中",
        "intent": intent
    }

# ✅ 主控分发器
def intent_dispatcher(intent):
    intent_type = intent.get("intent_type", "")

    if intent_type == "register_persona":
        return handle_register(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "chitchat":
        return handle_chitchat(intent)
    elif intent_type == "update_secret":
        return handle_update_secret(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的指令类型: {intent_type}",
            "intent": intent
        }

__all__ = ["intent_dispatcher"]
