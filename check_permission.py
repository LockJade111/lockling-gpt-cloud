import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 写入注册权限授权记录
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

# ✅ 撤销注册权限
def revoke_authorization(authorizer: str, grantee: str):
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

# ✅ 检查某个 persona 是否拥有注册新 persona 的授权
def check_register_permission(authorizer: str, grantee: str) -> bool:
    if not authorizer or not grantee:
        return False

    auth_string = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in auth_string.split(",") if x.strip()]
    return f"{authorizer}:{grantee}" in pairs

# ✅ 检查密钥口令是否正确
def check_secret_permission(persona: str, secret: str) -> bool:
    if not persona or not secret:
        return False

    auth_string = os.getenv("AUTHORIZED_SECRET", "")
    if not auth_string:
        return False

    entries = [x.strip() for x in auth_string.split(",") if x.strip()]
    for entry in entries:
        if ":" in entry:
            name, sec = entry.split(":", 1)
            if name == persona and sec == secret:
                return True
    return False
