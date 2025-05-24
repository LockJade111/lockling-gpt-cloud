import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 加载环境变量
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# ✅ 授权流程上下文缓存（可扩展为持久缓存）
auth_context = {}

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ⛩️ 分段式授权流程：
    if intent_type == "begin_auth":
        auth_context["stage"] = 1
        auth_context["grantee"] = intent.get("target")
        print(f"📜 [AUTH STAGE 1] 授权对象记录为：{auth_context['grantee']}")
        return False  # 暂不授权任何行为，等身份确认

    if intent_type == "confirm_identity":
        if intent.get("identity") == "将军":
            auth_context["stage"] = 2
            print("✅ [AUTH STAGE 2] 身份确认通过（将军）")
        else:
            print("❌ [AUTH STAGE 2] 身份确认失败")
        return False

    if intent_type == "confirm_secret":
        expected_secret = os.getenv("COMMANDER_SECRET", "").strip()
        provided = intent.get("secret", "").strip()

        if auth_context.get("stage") == 2 and provided == expected_secret:
            authorizer = "将军"
            grantee = auth_context.get("grantee")
            pair = f"{authorizer}:{grantee}"

            # ✅ 更新授权列表至 .env（简单追加版）
            env_path = ".env"
            authorized = os.getenv("AUTHORIZED_REGISTER", "")
            new_entries = set([x.strip() for x in authorized.split(",") if x.strip()])
            new_entries.add(pair)
            updated_line = f'AUTHORIZED_REGISTER={",".join(sorted(new_entries))}\n'

            # ✅ 写入（替换旧 AUTHORIZED_REGISTER）
            with open(env_path, "r") as f:
                lines = f.readlines()
            with open(env_path, "w") as f:
                for line in lines:
                    if not line.startswith("AUTHORIZED_REGISTER="):
                        f.write(line)
                f.write(updated_line)

            print(f"🎖️ [AUTH STAGE 3] 授权完成：{pair}")
            auth_context.clear()
            return True
        else:
            print("❌ [AUTH STAGE 3] 密钥验证失败")
            return False

    # ✅ 注册角色：检查是否获得将军授权
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 其他常规权限判断（数据库）
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
