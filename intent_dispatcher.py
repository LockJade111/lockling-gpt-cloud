import os
from check_permission import check_secret_permission
from persona_keys import register_persona
from src.supabase_logger import write_log_to_supabase
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        write_log_to_supabase(
            query=persona,
            reply=f"注册新 persona：{new_name}",
            intent_result=intent,
            status="success"
        )
        return {
            "status": "success",
            "reply": f"✅ 已注册新角色：{new_name}",
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

# ✅ 授权 intent
def handle_authorize(intent):
    print("📥 收到意图：authorize")

    source = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()

    if not source or not target:
        return {
            "status": "fail",
            "reply": "❌ 授权失败：缺少 source 或 target",
            "intent": intent
        }

    try:
        supabase.table("roles").insert({
            "source": source,
            "target": target,
            "granted_by": "系统"
        }).execute()

        # ✅ 添加字段：allow、reason
        intent["allow"] = True
        intent["reason"] = "授权成功"
        intent["target"] = target

        write_log_to_supabase(
            query=source,
            reply=f"授权 {target} 成功",
            intent_result=intent,
            status="success"
        )
        return {
            "status": "success",
            "reply": f"✅ 已授权 {target} 使用",
            "intent": intent
        }
    except Exception as e:
        intent["allow"] = False
        intent["reason"] = str(e)
        intent["target"] = target

        write_log_to_supabase(
            query=source,
            reply=str(e),
            intent_result=intent,
            status="fail"
        )
        return {
            "status": "fail",
            "reply": f"❌ 授权失败：{str(e)}",
            "intent": intent
        }

# ✅ 身份验证 intent
def handle_confirm_identity(intent):
    print("📥 收到意图：confirm_identity")
    target = intent.get("target", "")
    return {
        "status": "success",
        "reply": f"✅ {target} 身份验证通过",
        "intent": intent
    }

# ✅ 密钥确认 intent
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    return {
        "status": "success",
        "reply": f"✅ 密钥已确认",
        "intent": intent
    }

# ✅ 分发入口
def dispatcher(intent):
    intent_type = intent.get("intent_type", "")

    if intent_type == "register":
        return handle_register(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的指令类型: {intent_type}",
            "intent": intent
        }

__all__ = ["dispatcher"]
