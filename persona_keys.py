import bcrypt
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = "persona_keys"

# 初始化 Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 注册 persona
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
    existing = supabase.table(TABLE).select("persona").eq("persona", persona).execute()
    if existing.data:
        return False, f"角色 {persona} 已存在"

    try:
        hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
        result = supabase.table(TABLE).insert({
            "persona": persona,
            "secret_hash": hashed,
            "created_by": created_by,
            "role": role,
            "active": True,
            "failed_attempts": 0,
            "locked": False
        }).execute()
        return True, "✅ 注册成功"
    except Exception as e:
        return False, f"❌ 注册失败: {str(e)}"


# ✅ 验证 persona 密钥（带失败计数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
    try:
        result = supabase.table(TABLE).select("*").eq("persona", persona).execute()
        if not result.data:
            return False

        row = result.data[0]
        if row.get("locked"):
            return False

        stored_hash = row.get("secret_hash", "")
        if bcrypt.checkpw(input_secret.encode(), stored_hash.encode()):
            # 如果验证通过，重置失败次数
            supabase.table(TABLE).update({
                "failed_attempts": 0
            }).eq("persona", persona).execute()
            return True
        else:
            # 验证失败，失败次数 +1
            failed = row.get("failed_attempts", 0) + 1
            update_data = {"failed_attempts": failed}
            if failed >= 5:
                update_data["locked"] = True  # 超过5次锁定

            supabase.table(TABLE).update(update_data).eq("persona", persona).execute()
            return False
    except Exception:
        return False
