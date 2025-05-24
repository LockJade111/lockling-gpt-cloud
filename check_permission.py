import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 环境变量加载
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ✅ 授权操作判断：仅“将军” + 正确密钥才可执行授权
    if intent_type == "grant_permission":
        if persona != "将军":
            return False
        user_input = intent.get("source", "") if intent else ""
        secret = os.getenv("COMMANDER_SECRET", "")
        if secret not in user_input:
            return False
        return True

    # ✅ 注册角色：检查是否已获得授权
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 其余权限：查数据库角色权限
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
