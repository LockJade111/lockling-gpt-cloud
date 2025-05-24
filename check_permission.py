import os
from dotenv import load_dotenv

load_dotenv()

auth_context = {}

def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🧠 调试中: intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 阶段一：白名单身份信任 - 将军可执行初始验证流程
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"✅ 白名单将军放行阶段一: {intent_type}")
        return True

    # ✅ 阶段二：密钥验证并注册授权
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"

            # ✅ 更新 AUTHORIZED_REGISTER 列表
            env_path = ".env"
            authorized = os.getenv("AUTHORIZED_REGISTER", "")
            new_entries = set([x.strip() for x in authorized.split(",") if x.strip()])
            new_entries.add(pair)
            updated_line = f"AUTHORIZED_REGISTER={','.join(sorted(new_entries))}\n"

            # ✅ 写入 .env 文件
            with open(env_path, "r") as f:
                lines = f.readlines()
            with open(env_path, "w") as f:
                for line in lines:
                    if not line.startswith("AUTHORIZED_REGISTER="):
                        f.write(line)
                f.write(updated_line)

            print(f"✅ 授权授权成功，写入组合名: {pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 阶段三：注册阶段权限验证
    if required:
        authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
        authorized_pair = f"{required}:{persona}"
        result = authorized_pair in [x.strip() for x in authorized_list.split(",")]
        print(f"🔐 权限校验: {result}")
        return result

    return False


# ✅ 工具函数：写入注册授权关系（被 intent_dispatcher 调用）
def add_register_authorization(identity, target):
    env_path = ".env"
    key = f"{identity}:{target}"

    # 读取 .env 内容
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # 提取现有条目
    existing = ""
    for line in lines:
        if line.startswith("AUTHORIZED_REGISTER="):
            existing = line.strip().split("=", 1)[1]

    entries = [x.strip() for x in existing.split(",") if x.strip()]
    if key not in entries:
        entries.append(key)

    new_line = f'AUTHORIZED_REGISTER={",".join(entries)}\n'

    # 写入回 .env
    with open(env_path, "w") as f:
        for line in lines:
            if not line.startswith("AUTHORIZED_REGISTER="):
                f.write(line)
        f.write(new_line)

    print(f"✅ 写入授权记录: {key}")
    return True
