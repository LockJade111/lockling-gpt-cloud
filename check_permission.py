import os
from dotenv import load_dotenv

load_dotenv()

auth_context = {}

def check_permission(persona, required, intent_type=None, intent=None):
    print(f"🐛 调试中：intent_type={intent_type} | persona={persona}")

    # ✅ 白名单阶段：允许将军走 begin_auth / confirm_identity / confirm_secret
    if intent_type in ["begin_auth", "confirm_identity", "confirm_secret"] and persona.strip() == "将军":
    print(f"🟢 将军白名单放行 {intent_type}")
    return True
        
    # ✅ 密钥验证阶段（intent_type == confirm_secret）
    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip()
        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"

            # ✅ 写入 AUTHORIZED_REGISTER
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

            print(f"🎖️ 授权完成：{pair}")
            auth_context.clear()
            return True
        else:
            print("❌ 密钥验证失败")
            return False

    # ✅ 授权成功后的正式权限检查
    pair = f"{persona}:{intent.get('grantee', '')}"
    authorized = os.getenv("AUTHORIZED_REGISTER", "")
    if pair in [x.strip() for x in authorized.split(",") if x.strip()]:
        print(f"✅ {pair} 已获授权")
        return True

    print(f"❌ {persona} 无权执行 {intent_type}")
    return False
