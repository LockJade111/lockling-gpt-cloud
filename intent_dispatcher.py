import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    add_register_authorization,
    revoke_authorization,
)

# ✅ intent 处理：密钥确认
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent 处理：开始身份确认
def handle_begin_auth(intent):
    print("📥 收到意图：begin_auth")
    target = intent.get("target", "")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {target}，请告知身份。",
        "intent": intent
    }

# ✅ intent 处理：确认身份 → 注册授权
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

    return {
        "reply": "⚠️ 授权写入失败，请检查系统设置。",
        "intent": intent
    }

# ✅ intent 处理：撤销授权
def handle_revoke_identity(intent):
    print("📥 收到意图：revoke_identity")
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 撤销失败，缺少身份或目标。",
            "intent": intent
        }

    success = revoke_authorization(authorizer, grantee)
    if success:
        return {
            "reply": f"✅ 授权已取消：{authorizer} 撤销 {grantee} 的注册权限。",
            "intent": intent
        }

    return {
        "reply": f"⚠️ 撤销失败，可能未找到 {authorizer}:{grantee} 的授权记录。",
        "intent": intent
    }

# ✅ intent 处理：注册 persona（模拟写入或接入 Supabase）
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    name = intent.get("new_name", "").strip()

    if not name:
        return {
            "reply": "⚠️ 注册失败：缺少角色名称。",
            "intent": intent
        }

    # ✅ 可添加实际数据库写入逻辑（如 Supabase）
    print(f"✅ 注册 persona 成功: {name}")
    return {
        "reply": f"✅ persona '{name}' 注册成功，欢迎加入。",
        "intent": intent
    }

# ✅ 主分发函数
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    if not intent:
        return {
            "reply": "❌ 无法解析 intent。",
            "intent": {"intent": "unknown", "intent_type": "unknown"}
        }

    intent_type = intent.get("intent_type", "").strip()

    match intent_type:
        case "confirm_secret":
            return handle_confirm_secret(intent)
        case "begin_auth":
            return handle_begin_auth(intent)
        case "confirm_identity":
            return handle_confirm_identity(intent)
        case "revoke_identity":
            return handle_revoke_identity(intent)
        case "register_persona":
            return handle_register_persona(intent)
        case _:
            return {
                "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                "intent": intent
            }
