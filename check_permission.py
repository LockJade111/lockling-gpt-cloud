import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 环境加载
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ✅ 授权操作检查（如 grant_permission）
    if intent_type == "grant_permission":
        # 1. 必须是将军
        if persona != "将军":
            return False
        # 2. 必须包含“密钥”字样（从 intent 源信息中判断）
        user_input = intent.get("source", "") if intent else ""
        if "密钥" not in user_input:
            return False
        return True

    # ✅ 注册角色时，检查是否有将军授权
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")     # 发起授权的人
        grantee = persona                      # 当前尝试注册的人
        pair = f"{authorizer}:{grantee}"
        auth_list = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_list.split(",") if x.strip()]

    # ✅ 默认：查询 Supabase 权限表
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
