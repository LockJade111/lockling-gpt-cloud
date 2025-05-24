import os
from dotenv import load_dotenv

load_dotenv()

# ✅ 注册权限白名单（如果使用数据库权限系统，可跳过）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs", "register_persona"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 写入注册授权关系到 .env
def add_register_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"
    lines = []

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

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

    return True

# ✅ intent 处理函数：register_persona
def handle_register_persona(intent):
    new_name = intent.get("new_name", "").strip()
    source = intent.get("source", "")
    if new_name:
        return {
            "reply": f"✅ 新角色『{new_name}』注册成功，欢迎加入！",
            "intent": intent
        }
    else:
        return {
            "reply": "⚠️ 注册失败，请提供角色名称。",
            "intent": intent
        }

# ✅ 其他 intent 示例（保持不变或简化）
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

def handle_begin_auth(intent):
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {intent.get('target')}，请告知身份。",
        "intent": intent
    }

def handle_confirm_identity(intent):
    authorizer = intent.get("identity", "")
    grantee = intent.get("target", "")
    if authorizer and grantee:
        add_register_authorization(authorizer, grantee)
        return {
            "reply": f"✅ 授权成功：{authorizer} 授权 {grantee} 拥有注册权限。",
            "intent": intent
        }
    else:
        return {
            "reply": "⚠️ 授权失败，缺少身份或目标信息。",
            "intent": intent
        }

# ✅ 主调度函数：分发意图
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type", "")
    print(f"🧠 dispatch 调用中：intent_type={intent_type} | persona={persona}")

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
