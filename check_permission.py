import os
from dotenv import load_dotenv

# ✅ 加载 .env 环境变量
load_dotenv()

# ✅ 基础静态权限（角色预设权限）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取某 persona 的完整权限（静态 + 动态）
def get_persona_permissions(persona):
    base = permission_map.get(persona.strip(), [])
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")

    # ✅ 授权链判定（如：将军:司铃）
    for pair in authorized_pairs.split(","):
        if pair.strip().endswith(f":{persona}"):
            base.append("register_persona")
            break

    return sorted(set(base))


# ✅ 获取所有对 persona 授权过的人（反查）
def get_persona_authorizers(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.strip().endswith(f":{persona}")
    ]


# ✅ 获取 persona 授权过谁（正向）
def get_persona_grantees(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[1]
        for pair in authorized_pairs.split(",")
        if pair.strip().startswith(f"{persona}:")
    ]


# ✅ 添加授权关系（如：将军:司铃）写入 .env
def add_register_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 提取旧值
    existing_line = next((line for line in lines if line.startswith("AUTHORIZED_REGISTER=")), "")
    existing_value = existing_line.strip().split("=", 1)[1] if existing_line else ""
    pairs = [x.strip() for x in existing_value.split(",") if x.strip()]

    if key not in pairs:
        pairs.append(key)

    # 重写 .env
    new_line = f'AUTHORIZED_REGISTER={",".join(pairs)}\n'
    lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
    lines.append(new_line)

    with open(env_path, "w") as f:
        f.writelines(lines)

    return True


# ✅ 移除授权关系（撤销：将军:司铃）
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    existing_line = next((line for line in lines if line.startswith("AUTHORIZED_REGISTER=")), "")
    existing_value = existing_line.strip().split("=", 1)[1] if existing_line else ""
    pairs = [x.strip() for x in existing_value.split(",") if x.strip()]

    if key not in pairs:
        return False

    pairs = [x for x in pairs if x != key]
    new_line = f'AUTHORIZED_REGISTER={",".join(pairs)}\n'

    lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
    lines.append(new_line)

    with open(env_path, "w") as f:
        f.writelines(lines)

    return True
