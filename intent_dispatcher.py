import os

# ✅ 本地权限映射表（如切换到 Supabase 可替换查询）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 注册新 persona（写入 .env）
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
    return True

# ✅ intent: 密钥验证
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent: 身份确认起始
def handle_begin_auth(intent):
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {intent.get('target')}，请告知身份。",
        "intent": intent
    }

# ✅ intent: 授权注册权限
def handle_confirm_identity(intent):
    authorizer = intent.get("identity", "")
    grantee = intent.get("target", "")
    if not authorizer or not grantee:
        return {
            "reply": "⚠️ 授权失败，请检查身份与目标。",
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

    updated = f'AUTHORIZED_REGISTER={",".join(entries)}\n'
    lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
    with open(env_path, "w") as f:
        f.writelines(lines + [updated])

    return {
        "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册权限。",
        "intent": intent
    }

# ✅ intent: 注册新角色
def handle_register_persona(intent):
    name = intent.get("new_name", "").strip()
    if not name:
        return {
            "reply": "❌ 角色名不能为空。",
            "intent": intent
        }
    success = register_new_persona(name)
    if success:
        return {
            "reply": f"✅ 已成功注册新角色：{name}",
            "intent": intent
        }
    else:
        return {
            "reply": f"⚠️ 角色 {name} 已存在。",
            "intent": intent
        }

# ✅ 主调度函数
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type")
    print(f"🧭 dispatch 调用中：intent_type={intent_type} | persona={persona}")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    else:
        return {
            "reply": f"❌ 意图识别失败：dispatch_intents() 无法识别结构",
            "intent": {
                "intent": "unknown",
                "intent_type": "unknown",
                "source": intent.get("source", "")
            },
            "persona": persona
        }
