import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 环境加载
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ✅ 授权操作判断（grant_permission）
    if intent_type == "grant_permission":
        if persona != "将军":
            return False
        
        user_input = intent.get("source", "") or ""
        secret = os.getenv("COMMANDER_SECRET", "").strip()
        required_phrase = f"密钥{secret}"

        # ✅ Debug 输出
        print("🔍 [AUTH DEBUG] source: ", repr(user_input))
        print("🔍 [AUTH DEBUG] required_phrase: ", repr(required_phrase))

        # ✅ 精准容错判断：必须包含且以密钥前缀开头附近存在
        cleaned = user_input.replace(" ", "").replace("：", ":").replace("，", ",").strip()
        if required_phrase not in cleaned[:30]:  # 限定出现在开头30字符内
            print("❌ [AUTH FAIL] 授权口令不匹配")
            return False
        
        print("✅ [AUTH PASS] 授权验证通过")
        return True

    # ✅ 注册角色检查是否被授权
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 普通权限判断（Supabase 数据库）
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
