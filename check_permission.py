import os
from dotenv import load_dotenv
from supabase import create_client

# ✅ 加载环境变量
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str, intent_type: str = None, intent: dict = None) -> bool:
    # ✅ 特权授权判断逻辑
    if intent_type == "grant_permission":
        if persona != "将军":
            return False

        user_input = intent.get("source", "") or ""
        secret = os.getenv("COMMANDER_SECRET", "").strip()
        required_phrase = f"密钥{secret}"

        # ✅ Debug 打印（用于终端诊断）
        print("🔍 [AUTH DEBUG] source:", repr(user_input))
        print("🔍 [AUTH DEBUG] required_phrase:", repr(required_phrase))

        # ✅ 清理干扰字符并检查是否包含密钥短语
        cleaned = (
            user_input.replace(" ", "")
                      .replace("：", ":")
                      .replace("，", ",")
                      .replace("。", ".")
                      .strip()
        )

        if required_phrase not in cleaned[:30]:  # 限制位置前30字符范围内
            print("❌ [AUTH FAIL] 授权口令不匹配")
            return False

        print("✅ [AUTH PASS] 授权验证通过")
        return True

    # ✅ 注册角色：检查授权映射关系
    if intent_type == "register_persona" and intent:
        authorizer = intent.get("persona")
        grantee = persona
        pair = f"{authorizer}:{grantee}"
        auth_line = os.getenv("AUTHORIZED_REGISTER", "")
        return pair in [x.strip() for x in auth_line.split(",") if x.strip()]

    # ✅ 常规权限验证（数据库 roles 表）
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0].get("permissions", [])
    return required in perms
