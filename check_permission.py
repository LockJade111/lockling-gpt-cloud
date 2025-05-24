import os
from dotenv import load_dotenv

load_dotenv()
env_path = ".env"

# ✅ 密钥判断，将军等高权限身份的身份密钥
def check_secret_permission(persona: str, secret: str):
    key = f"SECRET_{persona.upper()}"
    stored = os.getenv(key, "").strip()
    print(f"[🔐] 密钥验证：persona={persona}，输入密钥={secret}，系统密钥={stored}")
    return secret == stored

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

    print(f"[✅] 授权记录写入成功：{key}")
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

    print(f"[⚠️] 已撤销授权：{key}")
    return True

# ✅ 判断某 persona 是否拥有注册新 persona 的权限
def check_register_permission(persona: str):
    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    entries = []
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            raw = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in raw.split(",") if x.strip()]

    authorized = [entry.split(":")[1] for entry in entries if ":" in entry]
    print(f"[🔍] 当前授权注册者列表：{authorized}")
    return persona in authorized
