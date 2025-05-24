import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 授权校验函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 阶段一：白名单身份信任
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"✅ 白名单将军放行阶段一: {intent_type}")
        return True

    # ✅ 阶段二：密钥验证注册授权
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            _add_authorization_env(pair)
            print(f"✅ 授权授权成功，写入组合名: {pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")

    # ✅ 阶段三：执行权限校验（基于授权表）
    authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
    key = f"{persona}:{intent.get('grantee')}" if intent else ""
    if f"{persona}:{required}" in authorized_list or key in authorized_list:
        print(f"✅ 授权匹配通过")
        return True

    print("❌ 权限不足，拒绝操作")
    return False


# ✅ 写入 AUTHORIZED_REGISTER 组合到 .env
def _add_authorization_env(pair):
    env_path = ".env"
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    new_entries = set(x.strip() for x in authorized.split(",") if x.strip())
    new_entries.add(pair)
    updated_line = f"AUTHORIZED_REGISTER={','.join(sorted(new_entries))}\n"

    with open(env_path, "r") as f:
        lines = f.readlines()
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(updated_line)


# ✅ 从 .env 中移除授权组合
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    new_entries = [x.strip() for x in authorized.split(",") if x.strip() and x.strip() != key]
    updated_line = f"AUTHORIZED_REGISTER={','.join(sorted(set(new_entries)))}\n"

    with open(env_path, "r") as f:
        lines = f.readlines()
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(updated_line)
    print(f"🧹 已移除授权：{key}")


# ✅ 获取 persona 拥有权限（注册后）
def get_persona_permissions(persona_name):
    key = f"PERMISSION_{persona_name}"
    env_path = ".env"
    if not os.path.exists(env_path):
        return []
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith(f"{key}="):
                return [x.strip() for x in line.strip().split("=", 1)[1].split(",")]
    return []

# ✅ 获取 persona 授予了谁（反查授权对象）
def get_persona_grantees(authorizer):
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    return [pair.split(":")[1] for pair in authorized.split(",") if pair.startswith(f"{authorizer}:")]
