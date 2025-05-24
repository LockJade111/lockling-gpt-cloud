import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 核心权限校验函数
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 阶段一：白名单直接放行
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"✅ 白名单将军放行阶段一: {intent_type}")
        return True

    # ✅ 阶段二：密钥验证 + 授权写入
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

    # ✅ 阶段三：通用权限验证（注册 / 创建）
    authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
    if not authorized_list:
        print("⚠️ 当前无授权记录")
        return False

    key = f"{persona}:{required}"
    if key in authorized_list:
        print(f"✅ 授权匹配通过: {key}")
        return True

    print("❌ 权限不足，拒绝操作")
    return False


# ✅ 写入授权组合到 .env 文件
def _add_authorization_env(pair):
    env_path = ".env"
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    entries = [x.strip() for x in authorized.split(",") if x.strip()]
    if pair not in entries:
        entries.append(pair)
    updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(updated_line)

    print(f"✅ 写入 .env: {updated_line.strip()}")


# ✅ 撤销授权
def revoke_authorization(authorizer, grantee):
    env_path = ".env"
    pair = f"{authorizer}:{grantee}"
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    entries = [x.strip() for x in authorized.split(",") if x.strip()]
    if pair in entries:
        entries.remove(pair)
    updated_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(updated_line)

    print(f"🧹 已撤销授权组合: {pair}")
    return True


# ✅ 查询拥有对某 persona 授权的人（授权人列表）
def get_persona_authorizers(persona):
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in authorized.split(",") if ":" in x]
    return sorted(set(a.split(":")[0] for a in pairs if a.split(":")[1] == persona))


# ✅ 查询该 persona 授权了谁（被授权列表）
def get_persona_grantees(persona):
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in authorized.split(",") if ":" in x]
    return sorted(set(a.split(":")[1] for a in pairs if a.split(":")[0] == persona))
