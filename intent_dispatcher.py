# intent_dispatcher.py

import os

# ✅ 本地测试权限映射表（若启用数据库版本，请改为 Supabase 查询）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 写入注册授权关系到 .env（如：将军:军师猫）
def add_register_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    # 读取 .env 内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 查找是否已存在
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

# ✅ intent 处理：密钥确认
def handle_confirm_secret(intent):
    return {
        "reply": "✅ 密钥验证通过，权限已激活。",
        "intent": intent
    }

# ✅ intent 处理：开始身份验证
def handle_begin_auth(intent):
    return {
        "reply": f"✅ 身份确认阶段开始，目标授权对象为 {intent.get('target')}，请告知身份。",
        "intent": intent
    }

# ✅ intent 处理：确认身份并执行注册授权
def handle_confirm_identity(intent):
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
        "reply": f"⚠️ 授权失败，请检查身份与目标。",
        "intent": intent
    }

# ✅ 主调度函数：根据意图类型分发处理
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent_type")

    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "begin_auth":
        return handle_begin_auth(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    else:
        return {
            "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
            "intent": intent
        }
