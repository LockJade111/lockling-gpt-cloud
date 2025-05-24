import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 加载环境变量
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ✅ 授权操作：只有将军 + 密钥方可授予权限
    if intent_type == "grant_permission":
        if persona != "将军":
            print("❌ 拒绝：非将军无法授予权限")
            return False

        user_input = intent.get("source", "") or ""
        secret = os.getenv("COMMANDER_SECRET", "").strip()
        required_phrase = f"密钥{secret}"

        # ✅ Debug 打印（终端确认真实内容）
        print("🔍 [DEBUG] raw source:", repr(user_input))
        print("🔍 [DEBUG] expected phrase:", repr(required_phrase))

        # ✅ 清理输入（去除空格、全角标点等）
        cleaned = (
            user_input.replace(" ", "")
                      .replace("：", ":")
                      .replace("，", ",")
                      .replace("。", ".")
                      .replace("\n", "")
                      .strip()
        )
        print("🔍 [DEBUG] cleaned source:", repr(cleaned))
        print("🔍 [DEBUG] searching phrase in first 30 chars:", repr(cleaned[:30]))

        if required_phrase not in cleaned[:30]:
            print("❌ [AUTH FAIL] 密钥验证失败")
            return False

        print("✅ [AUTH PASS] 授权密钥匹配成功")
        return True

    # ✅ 注册角色权限：检查是否存在授权绑定（env中授权行）
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 普通角色权限判断：从数据库中读取
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
