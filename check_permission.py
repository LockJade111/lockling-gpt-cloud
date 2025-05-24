import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 本地权限映射表，会根据授权写入动态更新
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance", "admin"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}


# ✅ 获取 persona 的权限列表（包含 .env 注册写入）
def get_persona_permissions(persona):
    return permission_map.get(persona.strip(), [])


# ✅ 获取谁授权给当前 persona（授权来源）
def get_persona_authorizers(persona):
    authorized_pairs = os.getenv("AUTHORIZED_REGISTER", "")
    return [
        pair.split(":")[0]
        for pair in authorized_pairs.split(",")
        if pair.endswith(f":{persona}")
    ]


# ✅ 添加授权记录，并同步写入 .env 与内存权限表
def add_register_authorization(authorizer, grantee, permission="register_persona"):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    # 读取旧内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 查找旧的授权对
    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    # 更新授权关系
    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    # 写入 .env 文件
    new_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'
    with open(env_path, "w") as f:
        lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
        f.writelines(lines + [new_line])

    # 更新权限映射表
    if grantee not in permission_map:
        permission_map[grantee] = []
    if permission not in permission_map[grantee]:
        permission_map[grantee].append(permission)


# ✅ 权限检查主函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🔍 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 白名单阶段，允许走初始认证流程
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 将军白名单放行阶段: {intent_type}")
        return True

    # ✅ 密钥认证授权阶段
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""

        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            add_register_authorization(authorizer, grantee)
            print(f"✅ 密钥验证成功，写入白名单: {pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 普通权限判断
    permissions = get_persona_permissions(persona)
    if required in permissions:
        print("✅ 权限验证通过")
        return True
    else:
        print("🔒 权限校验: False")
        return False
