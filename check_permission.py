import os

env_path = ".env"

# ✅ 精准读取 .env 文件中的变量值（支持中文变量名、emoji 等）
def read_env_key_strict(key):
    if not os.path.exists(env_path):
        return ""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                return line.strip().split("=", 1)[1].strip()
    return ""

# ✅ 身份密钥验证：如 persona=将军，secret=玉衡在手
def check_secret_permission(persona: str, secret: str):
    key = f"SECRET_{persona}"
    stored = read_env_key_strict(key)
    print(f"[🔐] 密钥验证：persona={persona}，输入密钥={secret}，系统密钥={stored}")
    return secret == stored

# ✅ 授权记录写入：如 将军 → 司铃 拥有注册权限
def add_register_authorization(authorizer: str, grantee: str):
    key = f"{authorizer}:{grantee}"
    if not os.path.exists(env_path):
        open(env_path, "w").close()

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    with open(env_path, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    print(f"[✅] 授权记录写入成功：{key}")
    return True

# ✅ 授权撤销：如将军移除 司铃 注册权限
def revoke_authorization(authorizer: str, grantee: str):
    key = f"{authorizer}:{grantee}"
    if not os.path.exists(env_path):
        return False

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key in entries:
        entries.remove(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    with open(env_path, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    print(f"[⚠️] 已撤销授权：{key}")
    return True

# ✅ 检查 persona 是否被授权注册 persona
def check_register_permission(persona: str):
    if not os.path.exists(env_path):
        return False

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            raw = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in raw.split(",") if x.strip()]

    authorized = [entry.split(":")[1] for entry in entries if ":" in entry]
    print(f"[🔍] 当前授权注册者列表：{authorized}")
    return persona in authorized
