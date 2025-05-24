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

# ✅ 主调度函数：根据意图类型分发处理
def dispatch_intents(intent: dict, persona: str = None) -> dict:
    intent_type = intent.get("intent")

    if intent_type == "log_finance":
        from finance_helper import log_finance
        return log_finance(intent, persona)

    elif intent_type == "log_customer":
        from customer_helper import log_customer
        return log_customer(intent, persona)

    elif intent_type == "schedule_event":
        from schedule_helper import schedule_event
        return schedule_event(intent, persona)

    elif intent_type == "save_memory":
        from memory_helper import save_memory
        return save_memory(intent, persona)

    elif intent_type == "grant_permission":
        from permission_helper import grant_permission
        return grant_permission(intent, persona)

    elif intent_type == "register_persona":
        from persona_helper import register_persona
        return register_persona(intent, persona)

    else:
        return {
            "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
            "intent": intent
        }
