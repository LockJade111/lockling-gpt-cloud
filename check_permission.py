import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 权限映射（可以替换为数据库存储）
permission_map = {
    "玉衡": ["query", "write", "schedule", "finance"],
    "司铃": ["schedule", "query", "email_notify"],
    "军师猫": ["query", "fallback", "logs"],
    "Lockling 锁灵": ["query", "write"],
    "小徒弟": ["schedule"]
}

# ✅ 自动添加权限（用于授权同步）
def sync_permission(persona, new_permission):
    if persona not in permission_map:
        permission_map[persona] = []
    if new_permission not in permission_map[persona]:
        permission_map[persona].append(new_permission)
        print(f"🟢 权限已同步添加：{persona} += {new_permission}")

# ✅ 自动移除权限（用于撤销）
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
        print(f"🧹 权限撤销完成：{grantee} -= {permission}")

# ✅ 权限判断核心入口
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🐛 调试中：intent_type={intent_type} | required={required} | persona={persona}")

    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        return True

    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            env_path = ".env"
            authorized = os.getenv("AUTHORIZED_REGISTER", "")
            new_entries = set([x.strip() for x in authorized.split(",") if x.strip()])
            new_entries.add(pair)
            updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(new_entries))}\n'
            with open(env_path, "r") as f:
                lines = f.readlines()
            with open(env_path, "w") as f:
                for line in lines:
                    if not line.startswith("AUTHORIZED_REGISTER="):
                        f.write(line)
                f.write(updated_line)
            print(f"🎖️ 授权成功：{pair}")
            sync_permission(grantee, "register_persona")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    if required:
        if required in permission_map.get(persona, []):
            print(f"✅ 权限校验通过：{persona} 拥有 {required}")
            return True
        else:
            print(f"⛔ 权限不足：{persona} 无 {required}")
            return False

    print("⛔ 权限判断未通过")
    return False

# ✅ 查询当前权限列表
def get_persona_permissions(persona):
    permissions = permission_map.get(persona, [])
    print(f"🔍 {persona} 当前权限：{permissions}")
    return permissions

# ✅ 查询授权人（.env）
def get_persona_authorizers(persona):
    authorized_by = []
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("AUTHORIZED_REGISTER="):
                    entries = line.strip().split("=", 1)[1].split(",")
                    for entry in entries:
                        parts = entry.strip().split(":")
                        if len(parts) == 2 and parts[1] == persona:
                            authorized_by.append(parts[0])
    print(f"🧭 {persona} 被授权于：{authorized_by}")
    return authorized_by

# ✅ 查询被授权人（.env）
def get_persona_grantees(authorizer):
    grantees = []
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("AUTHORIZED_REGISTER="):
                    entries = line.strip().split("=", 1)[1].split(",")
                    for entry in entries:
                        parts = entry.strip().split(":")
                        if len(parts) == 2 and parts[0] == authorizer:
                            grantees.append(parts[1])
    print(f"📜 {authorizer} 授权了：{grantees}")
    return grantees
