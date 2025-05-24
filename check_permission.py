import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🐛 调试中：intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 阶段一：白名单放行（将军执行初始授权流程）
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 白名单将军放行阶段一：{intent_type}")
        return True

    # ✅ 阶段二：密钥验证并注册授权
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip() if intent else ""
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"

            # 更新 AUTHORIZED_REGISTER 列表
            env_path = ".env"
            authorized = os.getenv("AUTHORIZED_REGISTER", "")
            new_entries = set([x.strip() for x in authorized.split(",") if x.strip()])
            new_entries.add(pair)
            updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(new_entries))}\n'

            # 写入 .env 文件
            with open(env_path, "r") as f:
                lines = f.readlines()
            with open(env_path, "w") as f:
                for line in lines:
                    if not line.startswith("AUTHORIZED_REGISTER="):
                        f.write(line)
                f.write(updated_line)

            print(f"🎖️ 授权成功，写入白名单：{pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 阶段三：通用权限验证（用于 register_persona 等）
    if required:
        authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
        pair = f"{persona}:{required}"
        if pair in [x.strip() for x in authorized_list.split(",") if x.strip()] or f"{persona}:*" in authorized_list:
            print(f"🟢 {persona} 被授权执行 {required}")
            return True
        else:
            print(f"⛔ {persona} 无权限执行 {required}")
            return False

    print("⛔ 未通过权限校验")
    return False
