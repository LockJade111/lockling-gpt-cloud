import bcrypt
import os
from supabase import create_client, Client

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE = "persona_keys"

# ✅ 注册 persona（支持写入角色，返回布尔值 + 消息）
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
    # 查重
    existing = supabase.table(TABLE).select("persona").eq("persona", persona).execute()
    if existing.data:
        return False, f"角色 {persona} 已存在"

    hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()

    try:
        result = supabase.table(TABLE).insert({
            "persona": persona,
            "secret_hash": hashed,
            "created_by": created_by,
            "role": role,
            "active": True,
            "failed_attempts": 0,
            "locked": False
        }).execute()
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"

# ✅ 验证 persona 密钥（含失败计数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
    try:
        result = supabase.table(TABLE).select("*").eq("persona", persona).eq("active", True).limit(1).execute()
        if not result.data:
            print(f"[❌] 无法找到 persona：{persona}")
            return False

        row = result.data[0]

        if row.get("locked"):
            print(f"[🔒] 账号已锁定：{persona}")
            return False

        stored_hash = row["secret_hash"]
        if bcrypt.checkpw(input_secret.encode(), stored_hash.encode()):
            supabase.table(TABLE).update({
                "failed_attempts": 0
            }).eq("persona", persona).execute()
            return True
        else:
            new_count = row.get("failed_attempts", 0) + 1
            update_data = {"failed_attempts": new_count}
            if new_count >= 5:
                update_data["locked"] = True
            supabase.table(TABLE).update(update_data).eq("persona", persona).execute()
            return False
    except Exception as e:
        print(f"[异常] 密钥验证异常: {e}")
        return False

# ✅ 可扩展：注销、删除等接口可后续添加
