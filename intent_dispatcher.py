# intent_dispatcher.py

import os

# ✅ 权限映射表（本地测试阶段使用，后续将改为 Supabase 查询）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling": ["query"],
    "小徒弟": ["schedule"]
}

# ✅ 写入授权关系到 .env
def add_register_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    # 读取现有 .env 内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 读取现有已授权数据
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

# ✅ 主函数处理所有意图
def dispatch_intents(intent: dict) -> dict:
    intent_type = intent.get("intent")

    # ✅ 注册角色
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

    # ✅ 授权注册权限：如“授权军师猫可以注册新角色”
    elif intent_type == "grant_permission":
        authorizer = intent.get("persona")
        grantee = intent.get("grantee")
        permission = intent.get("permission")

        if permission == "register_persona":
            added = add_register_authorization(authorizer, grantee)
            if added:
                return {
                    "reply": f"✅ {grantee} 已被 {authorizer} 授权注册新角色（写入 .env）"
                }
            else:
                return {
                    "reply": f"⚠️ {grantee} 授权已存在，无需重复写入"
                }

    # ✅ 示例意图：记录财务
    elif intent_type == "log_finance":
        return {
            "reply": f"🧾 [示例] 财务记录已保存。",
            "intent": intent
        }

    # ❌ 未知意图 fallback
    return {
        "reply": f"⚠️ 未知意图：{intent_type}",
        "intent": intent
    }
