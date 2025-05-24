import os
from dotenv import load_dotenv

# ✅ 加载 .env 环境变量（每次调用前重载确保最新）
def load_env():
    load_dotenv(dotenv_path=".env", override=True)

# ✅ 静态权限表（内建角色）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取某 persona 的完整权限（静态 + 动态授权）
def get_persona_permissions(persona):
    load_env()
    base = permission_map.get(persona.strip(), []).copy()
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    for pair in authorized_pairs.split(","):
        if pair.strip().endswith(f":{persona}"):
            base.append("register_persona")
            break
    return sorted(set(base))

# ✅ 判断某授权是否存在（如：将军:司铃）
def is_authorized(authorizer, grantee):
    load_env()
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    authorized_pairs = [x.strip() for x in authorized.split(",") if x.strip()]
    return f"{authorizer}:{grantee}" in authorized_pairs

# ✅ 添加授权记录（如：将军授权司铃）
def add_authorization_env(authorizer, grantee):
    load_env()
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

    return True

# ✅ 撤销授权（移除对应键）
def revoke_authorization(authorizer, grantee):
    load_env()
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        return False

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    old_entries = [x.strip() for x in existing.split(",") if x.strip()]
    new_entries = [x for x in old_entries if x != key]
    new_line = f'AUTHORIZED_REGISTER={",".join(new_entries)}\n'

    with open(env_path, "w") as f:
        lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
        f.writelines(lines + [new_line])

    return True

# ✅ 反查授权者（谁给他授权）
def get_persona_authorizers(persona):
    load_env()
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.strip().endswith(f":{persona}")
    ]

# ✅ 查询被授权人（他授权给谁）
def get_persona_grantees(persona):
    load_env()
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[1]
        for pair in authorized_pairs.split(",")
        if pair.strip().startswith(f"{persona}:")
    ]
