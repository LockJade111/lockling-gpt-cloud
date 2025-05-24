import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

# ✅ 授权写入 .env 文件
def _add_authorization_env(pair: str):
    env_path = ".env"
    if not os.path.exists(env_path):
        open(env_path, "w").close()

    with open(env_path, "r") as f:
        lines = f.readlines()

    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if pair not in entries:
        entries.append(pair)

    new_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

# ✅ 撤销授权（从 .env 移除）
def revoke_authorization(authorizer: str, grantee: str):
    env_path = ".env"
    key = f"{authorizer}:{grantee}"

    if not os.path.exists(env_path):
        return False

    with open(env_path, "r") as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]
            entries = [x.strip() for x in existing.split(",") if x.strip()]
            if key in entries:
                entries.remove(key)
                updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(entries))}\n'
                lines[i] = updated_line
                updated = True
                break

    if updated:
        with open(env_path, "w") as f:
            f.writelines(lines)
        print(f"✅ 撤销成功: {key}")
        return True

    print(f"⚠️ 无法撤销: {key} 不存在")
    return False

# ✅ 获取某 persona 拥有的所有权限（谁被他授权）
def get_persona_grantees(persona: str):
    raw = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in raw.split(",") if x.strip()]
    return [g.split(":")[1] for g in pairs if g.startswith(f"{persona}:")]

# ✅ 获取某 persona 被谁授权（谁授权了他）
def get_persona_authorizers(persona: str):
    raw = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in raw.split(",") if x.strip()]
    return [g.split(":")[0] for g in pairs if g.endswith(f":{persona}")]

# ✅ 获取 persona 当前允许执行的权限类型（如 register_persona）
def get_persona_permissions(persona: str):
    raw = os.getenv("AUTHORIZED_REGISTER", "")
    pairs = [x.strip() for x in raw.split(",") if x.strip()]
    return [g.split(":")[1] for g in pairs if g.startswith(f"{persona}:")]

# ✅ 权限校验主入口
def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type}, requires={required}, persona={persona}")

    # ✅ 白名单阶段放行
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"✅ 白名单放行阶段一: {intent_type}")
        return True

    # ✅ 密钥校验 + 授权写入
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"
            _add_authorization_env(pair)
            print(f"✅ 授权成功，写入组合: {pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥校验失败或阶段不符")

    # ✅ 标准授权验证（如 persona=将军 是否对司铃授权 register_persona）
    key = f"{persona}:{required}"
    authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
    if key in authorized_list:
        print(f"✅ 授权验证通过: {key}")
        return True

    print("❌ 权限不足，拒绝操作")
    return False
