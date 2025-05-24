import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 授权记录写入 .env 文件
def add_register_authorization(authorizer: str, grantee: str):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        open(env_path, "w").close()

    with open(env_path, "r") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    return True

# ✅ 从 .env 文件撤销授权
def revoke_authorization(authorizer: str, grantee: str):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in existing.split(",") if x.strip() and x.strip() != key]
            updated_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(updated_lines)

    return True

# ✅ 获取授权该 grantee 的所有 authorizer
def get_persona_authorizers(grantee: str) -> list:
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in authorized.split(",") if x.strip()]
    authorizers = [p.split(":")[0] for p in pairs if p.endswith(f":{grantee}")]
    return sorted(set(authorizers))

# ✅ 获取某个 authorizer 授权过的对象
def get_persona_grantees(authorizer: str) -> list:
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in authorized.split(",") if x.strip()]
    grantees = [p.split(":")[1] for p in pairs if p.startswith(f"{authorizer}:")]
    return sorted(set(grantees))

# ✅ 获取 persona 拥有的权限
def get_persona_permissions(persona: str) -> list:
    permission_map = {
        "玉衡": ["query", "write", "schedule", "finance", "admin"],
        "司铃": ["schedule", "query", "email_notify"],
        "军师猫": ["query", "fallback", "logs"],
        "Lockling 锁灵": ["query", "write"],
        "小徒弟": ["schedule"]
    }

    # 若被授权，则默认拥有 register_persona 权限
    authorizers = get_persona_authorizers(persona)
    if authorizers:
        base = permission_map.get(persona, [])
        return sorted(set(base + ["register_persona"]))

    return permission_map.get(persona, [])

# ✅ 主权限校验逻辑
def check_permission(persona, required=None, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 白名单将军放行阶段：{intent_type}")
        return True

    if required is None:
        return True

    current_permissions = get_persona_permissions(persona)
    print(f"🔐 权限校验中: 当前权限={current_permissions}")
    if required in current_permissions:
        return True

    print(f"🚫 权限拒绝: {persona} 不具备权限 {required}")
    return False
