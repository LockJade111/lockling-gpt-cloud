from check_permission import check_secret_permission
from persona_keys import (
    register_persona,
    check_persona_secret,
    revoke_persona,
    delete_persona,
    unlock_persona
)

from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ✅ 密钥确认
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    persona = intent.get("persona", "").strip()
    secret = intent.get("secret", "").strip()

    if check_persona_secret(persona, secret):
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
    secret = intent.get("secret", "").strip()

    if not new_name:
        return {
            "status": "fail",
            "reply": "❌ 注册失败：未指定新 persona 名称。",
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
        return {
            "status": "success",
            "reply": f"✅ 已注册新角色：{new_name}",
            "intent": intent
        }
    except Exception as e:
        return {
            "status": "fail",
            "reply": f"❌ 注册失败：{str(e)}",
            "intent": intent
        }


# ✅ 授权权限 intent
def handle_authorize(intent):
    print("📥 收到意图：authorize")
    target = intent.get("target", "").strip()
    permission = intent.get("permission", "").strip()

    if not target or not permission:
        return {
            "status": "fail",
            "reply": "❌ 授权失败：缺少目标或权限类型。",
            "intent": intent
        }

    try:
        res = supabase.table("roles").select("permissions").eq("role", target).execute()
        if not res.data:
            return {
                "status": "fail",
                "reply": f"❌ 授权失败：目标角色 {target} 不存在。",
                "intent": intent
            }

        current = res.data[0].get("permissions", [])
        if permission in current:
            return {
                "status": "info",
                "reply": f"⚠️ {target} 已拥有 {permission} 权限。",
                "intent": intent
            }

        updated = current + [permission]
        supabase.table("roles").update({"permissions": updated}).eq("role", target).execute()
        return {
            "status": "success",
            "reply": f"✅ 已授权 {target} 拥有 {permission} 权限。",
            "intent": intent
        }

    except Exception as e:
        return {
            "status": "fail",
            "reply": f"❌ 授权失败：{str(e)}",
            "intent": intent
        }


# ✅ 撤销权限 intent
def handle_revoke(intent):
    print("📥 收到意图：revoke")
    target = intent.get("target", "").strip()
    permission = intent.get("permission", "").strip()

    if not target or not permission:
        return {
            "status": "fail",
            "reply": "❌ 撤销失败：缺少目标或权限类型。",
            "intent": intent
        }

    try:
        res = supabase.table("roles").select("permissions").eq("role", target).execute()
        if not res.data:
            return {
                "status": "fail",
                "reply": f"❌ 撤销失败：目标角色 {target} 不存在。",
                "intent": intent
            }

        current = res.data[0].get("permissions", [])
        if permission not in current:
            return {
                "status": "info",
                "reply": f"⚠️ {target} 原本就不具备 {permission} 权限。",
                "intent": intent
            }

        updated = [p for p in current if p != permission]
        supabase.table("roles").update({"permissions": updated}).eq("role", target).execute()
        return {
            "status": "success",
            "reply": f"✅ 已撤销 {target} 的 {permission} 权限。",
            "intent": intent
        }

    except Exception as e:
        return {
            "status": "fail",
            "reply": f"❌ 撤销失败：{str(e)}",
            "intent": intent
        }


# ✅ 主调度器
def dispatch(intent: dict):
    intent_type = intent.get("intent_type", "")
    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "revoke":
        return handle_revoke(intent)
    else:
        return {
            "status": "info",
            "reply": f"🤖 尚未支持的意图类型：{intent_type}",
            "intent": intent
        }
