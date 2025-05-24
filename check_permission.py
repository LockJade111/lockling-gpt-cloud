import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 写入授权记录到 .env 文件
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

# ✅ 撤销授权（从 .env 中移除指定授权对）
def revoke_authorization(authorizer: str, grantee: str):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in existing.split(",") if x.strip() and x.strip() != key]
            lines[i] = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    with open(env_path, "w") as f:
        f.writelines(lines)

    return True

# ✅ 获取某个 persona 的所有授权者
def get_persona_authorizers(grantee: str):
    env_path = ".env"
    if not os.path.exists(env_path):
        return []

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("AUTHORIZED_REGISTER="):
                raw = line.strip().split("=", 1)[1]
                entries = [x.strip() for x in raw.split(",") if x.strip()]
                return [auth.split(":")[0] for auth in entries if auth.endswith(f":{grantee}")]
    return []

# ✅ 获取某个 persona 授权了哪些人
def get_persona_grantees(authorizer: str):
    env_path = ".env"
    if not os.path.exists(env_path):
        return []

    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("AUTHORIZED_REGISTER="):
                raw = line.strip().split("=", 1)[1]
                entries = [x.strip() for x in raw.split(",") if x.strip()]
                return [auth.split(":")[1] for auth in entries if auth.startswith(f"{authorizer}:")]
    return []

# ✅ 权限判断入口函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # 白名单阶段 - 将军可跳过所有权限判断
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 白名单将军放行阶段: {intent_type}")
        return True

    # 注册授权阶段
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            add_register_authorization(authorizer, grantee)
            auth_context.clear()
            print(f"✅ 密钥验证通过，写入角色名: {pair}")
            return True
        else:
            print(f"❌ 密钥验证失败或阶段错误")
            return False

    # 正式权限判断
    if not required:
        return True

    authorized = get_persona_authorizers(persona)
    print(f"🔐 当前 {persona} 被以下角色授权: {authorized}")
    return any(auth in authorized for auth in required)
