import os
from dotenv import load_dotenv

load_dotenv()

# ✅ 权限映射表
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 写入授权关系
def add_register_authorization(authorizer, grantee):
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

    new_line = f"AUTHORIZED_REGISTER={','.join(entries)}\n"
    with open(env_path, "w") as f:
        lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
        f.writelines(lines + [new_line])

    return True

# ✅ intent: confirm_secret
def handle_confirm_secret(intent):
    print("🐛 调试：处理 confirm_secret")
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent: begin_auth
def handle_begin_auth(intent):
    print("🐛 调试：处理 begin_auth")
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {intent.get('target')}，请告知身份。",
        "intent": intent
    }

# ✅ intent: confirm_identity
def handle_confirm_identity(intent):
    print("🐛 调试：处理 confirm_identity")
    authorizer = intent.get("identity", "")
    grantee = intent.get("target", "")
    if authorizer and grantee:
        success = add_register_authorization(authorizer, grantee)
        if success:
            return {
                "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册角色权限。",
                "intent": intent
            }
    return {
        "reply": "⚠️ 授权失败，请检查身份与目标。",
        "intent": intent
    }

# ✅ intent: register_persona
def handle_register_persona(intent):
    print("🐛 调试：处理 register_persona")
    new_name = intent.get("new_name")
    if new_name:
        return {
            "reply": f"✅ 新角色已注册成功：{new_name}。",
            "intent": intent
        }
    else:
        return {
            "reply": "⚠️ 注册失败，缺少角色名称。",
            "intent": intent
        }

# ✅ 主调度函数
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type")
    print(f"🧪 dispatch 调试：intent_type={intent_type} | intent={intent}")

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
                "source": intent.get("source", "无来源")
            },
            "persona": persona
        }
