# intent_dispatcher.py

# ✅ 内存权限映射表（后期可存入 Supabase）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling": ["query"],
    "小徒弟": ["schedule"]
}

def dispatch_intents(intent: dict) -> dict:
    intent_type = intent.get("intent")

    # ✅ 处理角色注册请求
    if intent_type == "register_persona":
        new_name = intent.get("new_name", "未知")
        permissions = intent.get("permissions", [])
        tone = intent.get("tone", "默认")

        if new_name not in permission_map:
            permission_map[new_name] = permissions
        else:
            for p in permissions:
                if p not in permission_map[new_name]:
                    permission_map[new_name].append(p)

        return {
            "reply": f"✅ 已注册角色 {new_name}，语气为 {tone}，权限为 {permissions}",
            "registered_persona": new_name,
            "permissions": permissions,
            "tone": tone
        }

    # ✅ 示例处理：记录财务
    elif intent_type == "log_finance":
        return {
            "reply": f"🧾 [示例] 财务记录已保存。",
            "intent": intent
        }

    # ❗未识别 fallback
    return {
        "reply": f"⚠️ 未知意图：{intent_type}",
        "intent": intent
    }
