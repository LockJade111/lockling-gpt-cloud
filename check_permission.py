import os
from dotenv import load_dotenv

load_dotenv()

auth_context = {}

def check_permission(persona, required, intent_type=None, intent=None):
    # ✅ 白名单阶段：允许将军走 begin_auth / confirm_identity / confirm_secret
    if intent_type in ["begin_auth", "confirm_identity"] and persona == "将军":
        print(f"🟢 将军白名单放行 {intent_type}")
        return True

    # ✅ 密钥验证
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

    # ✅ begin_auth 启动授权流程（stage 1）
    if intent_type == "begin_auth":
        auth_context["stage"] = 1
        auth_context["grantee"] = intent.get("target")
        print(f"📜 授权对象记录为：{auth_context['grantee']}")
        return True  # ← 这就是修复关键！允许执行 intent 响应，而不是拒绝

    # ✅ 注册角色：检查 AUTHORIZED_REGISTER 是否包含
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 其他权限判断走 Supabase（可扩展）
    return False  # 默认拒绝
