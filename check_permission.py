import os
from dotenv import load_dotenv

load_dotenv()
env_path = ".env"

# ✅ 写入注册权限授权记录
def add_register_authorization(authorizer: str, grantee: str):
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

# ✅ 撤销注册权限
def revoke_authorization(authorizer: str, grantee: str):
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key in entries:
        entries.remove(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    return True

# ✅ 查询是否已获得注册授权
def has_register_authorization(authorizer: str, grantee: str) -> bool:
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("AUTHORIZED_REGISTER="):
                existing = line.strip().split("=", 1)[1]
                entries = [x.strip() for x in existing.split(",") if x.strip()]
                return key in entries

    return False

# ✅ 查询某 persona 是否设置密钥
def check_secret_for_persona(persona: str, secret: str) -> bool:
    persona_key = f"PERSONA_{persona}"
    actual_secret = os.getenv(persona_key)
    return actual_secret == secret
