import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表，会根据授权写入动态更新
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin", "register_persona"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 获取某 persona 拥有的权限列表
def get_persona_permissions(persona):
    return permission_map.get(persona.strip(), [])

# ✅ 获取被谁授权（授权者列表）
def get_persona_authorizers(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.endswith(f":{persona}")
    ]

# ✅ 获取已被该 persona 授权的对象列表（grantee）
def get_persona_grantees(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[1]
        for pair in authorized_pairs.split(",")
        if pair.startswith(f"{persona}:")
    ]

# ✅ 添加授权记录（如：将军授权军师猫）
def add_register_authorization(authorizer, grantee, permission="register_persona"):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    # 读取 .env 文件内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 读取已有的授权对
    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    # 写入新的 .env 内容
    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    return True

# ✅ 检查权限通行逻辑
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 白名单阶段：无需密钥，直接通行
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona == "将军":
        print(f"🟢 将军白名单放行: {intent_type}")
        return True

    # ✅ 密钥阶段（confirm_secret）：验证身份后通行
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            auth_context["authorizer"] = "将军"
            auth_context["grantee"] = auth_context.get("grantee")
            print("✅ 密钥验证成功")
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 授权判断阶段
    # 从权限映射中获取角色权限列表
    permissions = get_persona_permissions(persona)

    if required in permissions:
        print("✅ 权限检查通过（来自映射表）")
        return True

    # ✅ 支持注册授权对（如：将军:军师猫）
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    grantee = persona
    authorizers = get_persona_authorizers(grantee)

    for authorizer in authorizers:
        if required in get_persona_permissions(authorizer):
            print("✅ 权限继承检查通过")
            return True

    print("❌ 权限不足，拒绝操作")
    return False

