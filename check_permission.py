import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表（静态 + 动态授权）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取 persona 拥有的权限
def get_persona_permissions(persona):
    return permission_map.get(persona.strip(), [])

# ✅ 获取该 persona 被谁授权（返回所有授权者）
def get_persona_authorizers(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.endswith(f":{persona}")
    ]

# ✅ 获取该 persona 授权了谁（返回被授权对象列表）
def get_persona_grantees(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[1]
        for pair in authorized_pairs.split(",")
        if pair.startswith(f"{persona}:")
    ]

# ✅ 添加授权记录，将 {authorizer}:{grantee} 写入 .env
def add_register_authorization(authorizer, grantee, permission="register_persona"):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    # 读取 .env 内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 找到原始授权行
    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    updated_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'

    # 重写 .env
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(updated_line)

    return True

# ✅ 撤销授权，将 {authorizer}:{grantee} 从 .env 中删除
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    pair = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in existing.split(",") if x.strip() and x.strip() != pair]
            new_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(updated_lines)

    return True

# ✅ 权限检查（在 main.py 中会调用）
def has_permission(persona, required):
    if not required:
        return True
    permissions = get_persona_permissions(persona)
    return required in permissions
