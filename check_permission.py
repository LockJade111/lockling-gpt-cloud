import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表（会被授权写入同步更新）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 添加注册授权，并同步写入 .env 和 permission_map
def add_register_authorization(authorizer, grantee, permission="register_persona"):
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

    if grantee not in permission_map:
        permission_map[grantee] = []
    if permission not in permission_map[grantee]:
        permission_map[grantee].append(permission)


# ✅ 获取某个角色的权限列表（供 UI 或日志显示）
def get_persona_permissions(persona: str) -> list:
    from dotenv import load_dotenv
    load_dotenv()

    persona = persona.strip()
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    entries = [x.strip() for x in authorized.split(",") if ":" in x]
    granted_targets = [pair.split(":")[1] for pair in entries if pair.startswith(f"{persona}:")]

    default_roles = {
        "将军": ["admin", "query", "write", "register"],
        "军师猫": ["query", "register"],
        "司铃": ["query", "schedule"],
    }

    return default_roles.get(persona, []) + (["register"] if granted_targets else [])


# ✅ 主权限判断函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 白名单阶段
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 将军白名单放行: {intent_type}")
        return True

    # ✅ 密钥验证阶段
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            add_register_authorization(authorizer, grantee)
            auth_context.clear()
            print(f"✅ 密钥验证成功，写入白名单: {pair}")
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 权限判断
    permissions = get_persona_permissions(persona)
    print(f"🔐 权限核验: {permissions}")
    if required in permissions:
        return True
    else:
        print("⛔ 权限不足")
        return False
