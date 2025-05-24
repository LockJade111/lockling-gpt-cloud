import os
from check_permission import (
    get_persona_permissions,
    get_persona_authorizers,
    get_persona_grantees,
    revoke_authorization,
    sync_permission
)

# ✅ 注册新 persona（写入 .env 标记激活）
def register_new_persona(name: str):
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    key = f"PERSONA_{name}=active\n"
    if any(line.startswith(f"PERSONA_{name}=") for line in lines):
        return False

    lines.append(key)
    with open(env_path, "w") as f:
        f.writelines(lines)
    print(f"✨ 新 persona 注册完成：{name}")
    return True

# ✅ intent: 密钥验证确认
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent: 授权阶段起始
def handle_begin_auth(intent):
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {intent.get('target')}，请告知身份。",
        "intent": intent
    }

# ✅ intent: 授权某角色可注册新角色
def handle_confirm_identity(intent):
    authorizer = intent.get("identity", "").strip()
    grantee = intent.get("target", "").strip()
    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 授权失败，信息不完整。",
            "intent": intent
        }

    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'

    with open(env_path, "w") as f:
        lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
        f.writelines(lines + [new_line])

    # ✅ 同步权限
    sync_permission(grantee, "register_persona")

    return {
        "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册角色权限。",
        "intent": intent
    }

# ✅ intent: 注册 persona
def handle_register_persona(intent):
    name = intent.get("new_name", "").strip()
    source = intent.get("source", "").strip()

    if not name:
        return {
            "reply": "⚠️ 注册失败，请提供角色名称。",
            "intent": intent
        }

    success = register_new_persona(name)
    if success:
        return {
            "reply": f"✅ 角色 {name} 已注册成功（来源：{source}）",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 注册失败：角色 {name} 已存在或写入失败。",
            "intent": intent
        }

# ✅ intent: 查询权限和授权来源
def handle_query_permissions(intent):
    target = intent.get("target", "").strip() or intent.get("source", "").strip()
    if not target:
        return {
            "reply": "⚠️ 查询失败，未指定角色。",
            "intent": intent
        }

    permissions = get_persona_permissions(target)
    authorizers = get_persona_authorizers(target)

    return {
        "reply": f"🔐 {target} 当前权限：{permissions}\n🧭 授权自：{authorizers}",
        "intent": intent
    }

# ✅ intent: 撤销权限
def handle_revoke_permission(intent):
    authorizer = intent.get("authorizer", "").strip()
    grantee = intent.get("target", "").strip()
    permission = intent.get("permission", "register_persona").strip()

    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 撤销失败，参数不完整。",
            "intent": intent
        }

    revoke_authorization(authorizer, grantee, permission)

    return {
        "reply": f"✅ {authorizer} 已撤销 {grantee} 的权限：{permission}",
        "intent": intent
    }

# ✅ 主分发器
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "").strip()
    print(f"🐛 分发调试中：intent_type={intent_type}, persona={persona}")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    elif intent_type == "query_permissions":
        return handle_query_permissions(intent)
    elif intent_type == "revoke_permission":
        return handle_revoke_permission(intent)
    else:
        return {
            "reply": f"❌ dispatch_intents 无法识别类型：{intent_type}",
            "intent": {
                "intent": "unknown",
                "intent_type": intent_type,
                "source": intent.get("source", "")
            },
            "persona": persona
        }
