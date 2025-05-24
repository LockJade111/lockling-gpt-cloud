import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 权限映射（本地内存，用于演示）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 写入注册授权到 .env 并同步权限
def add_register_authorization(authorizer, grantee, permission="register_persona"):
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

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'
    with open(env_path, "w") as f:
        lines = [line for line in lines if not line.startswith("AUTHORIZED_REGISTER=")]
        f.writelines(lines + [new_line])

    if grantee not in permission_map:
        permission_map[grantee] = []
    if permission not in permission_map[grantee]:
        permission_map[grantee].append(permission)

    print(f"✅ 授权成功：{key} -> {permission}")
    return True

# ✅ 撤销授权
def revoke_authorization(authorizer, grantee, permission="register_persona"):
    env_path = ".env"
    pair = f"{authorizer}:{grantee}"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
        updated_lines = []
        for line in lines:
            if line.startswith("AUTHORIZED_REGISTER="):
                entries = line.strip().split("=", 1)[1].split(",")
                entries = [x.strip() for x in entries if x.strip() and x.strip() != pair]
                updated_lines.append(f'AUTHORIZED_REGISTER={",".join(entries)}\n')
            else:
                updated_lines.append(line)
        with open(env_path, "w") as f:
            f.writelines(updated_lines)
        print(f"🔻 授权关系已删除：{pair}")

    if grantee in permission_map and permission in permission_map[grantee]:
        permission_map[grantee].remove(permission)

# ✅ 主权限判断函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🔍 调试中：intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 白名单身份：将军直接放行敏感操作
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 白名单将军放行阶段：{intent_type}")
        return True

    # ✅ 密钥验证：confirm_secret
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if provided == expected_secret:
            auth_context["confirmed"] = True
            auth_context["stage"] = 2
            auth_context["grantee"] = intent.get("grantee") or ""
            auth_context["identity"] = persona
            print(f"🟢 密钥验证成功，身份={persona}，授权目标={auth_context['grantee']}")
            return True
        else:
            print("❌ 密钥错误或缺失")
            return False

    # ✅ 注册授权阶段：confirm_identity
    if intent_type == "confirm_identity":
        if auth_context.get("confirmed") and auth_context.get("stage") == 2:
            if auth_context.get("identity") == persona:
                print("🟢 身份校验通过，允许执行注册授权")
                return True
            else:
                print("❌ 身份不一致")
                return False
        else:
            print("❌ 未通过密钥验证阶段")
            return False

    # ✅ 正式权限判断（支持 register_persona 等）
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    authorized_list = [x.strip() for x in authorized.split(",") if x.strip()]
    pair = f"{persona}:{intent.get('target')}" if intent else ""
    if required == "register_persona" and pair in authorized_list:
        print(f"🟢 授权对已注册：{pair}")
        return True

    # ✅ 直接权限列表检查（非授权绑定）
    if required in permission_map.get(persona, []):
        print(f"✅ 权限校验通过：{persona} 包含 {required}")
        return True

    print("⛔ 权限校验：False")
    return False
