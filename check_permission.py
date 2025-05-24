import os
from dotenv import load_dotenv

load_dotenv()
auth_context = {}

def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🐛 调试中：intent_type={intent_type} | required={required} | persona={persona}")

    # ✅ 阶段一：白名单放行 - 将军可执行初始验证流程
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
        print(f"🟢 白名单将军放行阶段一：{intent_type}")
        return True

    # ✅ 阶段二：密钥验证并注册授权
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip()
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"

            # 写入 AUTHORIZED_REGISTER 环境变量
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

            print(f"🎖️ 授权成功，写入白名单：{pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败或阶段错误")
            return False

    # ✅ 阶段三：判断是否在授权表中
    authorized_list = os.getenv("AUTHORIZED_REGISTER", "")
    if f"{persona}:{intent.get('grantee')}" in authorized_list.split(","):
        print(f"✅ 已授权的注册者：{persona} 可为 {intent.get('grantee')} 执行 {intent_type}")
        return True

    # 默认拒绝
    print(f"❌ 未通过权限系统，拒绝操作: intent_type={intent_type}, required={required}")
    return False
