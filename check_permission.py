import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表（静态权限 + 动态授权扩展）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取 persona 拥有的权限（静态 + 动态）
def get_persona_permissions(persona):
    base = permission_map.get(persona.strip(), [])
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    if any(pair.strip() == f"{auth}:{persona}" for pair in authorized_pairs.split(",") if pair.strip()):
        base += ["register_persona"]
    return sorted(set(base))

# ✅ 获取 persona 被哪些人授权过（反查）
def get_persona_authorizers(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.strip().endswith(f":{persona}")
    ]

# ✅ 获取 persona 授权过哪些人
def get_persona_grantees(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[1]
        for pair in authorized_pairs.split(",")
        if pair.strip().startswith(f"{persona}:")
    ]

# ✅ 添加授权关系 authorizer:grantee 到 .env
def add_register_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 查找旧值
    authorized_line = next((line for line in lines if line.startswith("AUTHORIZED_REGISTER=")), "")
    current_values = authorized_line.strip().split("=", 1)[1] if authorized_line else ""
    entries = [x.strip() for x in current_values.split(",") if x.strip()]

    # 添加并去重
    if key not in entries:
        entries.append(key)

    updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(set(entries)))}\n'
    new_lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
    new_lines.append(updated_line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    return True

# ✅ 撤销授权（从 .env 移除 authorizer:grantee）
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    authorized_line = next((line for line in lines if line.startswith("AUTHORIZED_REGISTER=")), "")
    current_values = authorized_line.strip().split("=", 1)[1] if authorized_line else ""
    entries = [x.strip() for x in current_values.split(",") if x.strip()]
    if key not in entries:
        return False

    entries.remove(key)
    updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(set(entries)))}\n'
    new_lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
    new_lines.append(updated_line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    return True
