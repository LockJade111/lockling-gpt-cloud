import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表（静态权限 + 动态授权覆盖）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取 persona 拥有的权限（包含静态 + 动态）
def get_persona_permissions(persona):
    base = permission_map.get(persona.strip(), [])
    # 若注册权限被授权，动态加入
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    if any(pair.strip() == f"{auth}:{persona}" for pair in authorized_pairs.split(",") for auth in permission_map):
        base = base + ["register_persona"]
    return sorted(set(base))  # 去重 + 排序

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

# ✅ 添加授权记录（{authorizer}:{grantee}）写入 .env
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

    pairs = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in pairs:
        pairs.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(set(pairs)))}\n'

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    return True

# ✅ 移除授权记录（撤销授权）
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    pairs = [x.strip() for x in existing.split(",") if x.strip()]
    if key in pairs:
        pairs.remove(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(set(pairs)))}\n'

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    return True
