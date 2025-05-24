import bcrypt
import os
from supabase import create_client, Client

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE = "persona_keys"

# ✅ 注册 persona（含角色）
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
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
    return result

# ✅ 验证 persona 密钥（含失败计数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
    try:
        result = supabase.table(TABLE).select("*").eq("persona", persona).eq("active", True).limit(1).execute()
        if not result.data:
            print(f"[❌] 无法找到 persona：{persona}")
            return False

        row = result.data[0]

        # ✅ 已锁定的账号拒绝验证
        if row.get("locked"):
            print(f"[🔒] 账号已锁定：{persona}")
            return False

        stored_hash = row["secret_hash"]
        if bcrypt.checkpw(input_secret.encode(), stored_hash.encode()):
            # ✅ 验证成功，重置失败次数
            supabase.table(TABLE).update({
                "failed_attempts": 0
            }).eq("persona", persona).execute()
            print(f"[✅] 密钥验证成功：{persona}")
            return True
        else:
            # ❌ 验证失败：更新失败计数 + 如有必要锁定
            failed = row.get("failed_attempts", 0) + 1
            update_payload = {"failed_attempts": failed}
            if failed >= 5:
                update_payload["locked"] = True
                print(f"[⛔️] 失败次数过多，账号已锁定：{persona}")

            supabase.table(TABLE).update(update_payload).eq("persona", persona).execute()
            print(f"[❌] 密钥错误，当前失败次数：{failed}")
            return False

    except Exception as e:
        print(f"[⚠️] 验证异常：{e}")
        return False

# ✅ 撤销 persona（禁用注册权限）
def revoke_persona(persona: str):
    try:
        result = supabase.table(TABLE).update({"active": False}).eq("persona", persona).execute()
        return result
    except Exception as e:
        print(f"[❌] 撤销失败: {e}")
        return None

# ✅ 删除 persona（从数据库中移除记录）
def delete_persona(persona: str):
    try:
        result = supabase.table(TABLE).delete().eq("persona", persona).execute()
        return result
    except Exception as e:
        print(f"[❌] 删除失败: {e}")
        return None

# ✅ 获取 persona 角色
def get_persona_role(persona: str) -> str:
    try:
        result = supabase.table(TABLE).select("role").eq("persona", persona).limit(1).execute()
        if result.data:
            return result.data[0].get("role", "unknown")
    except Exception as e:
        print(f"[❌] 获取角色失败: {e}")
    return "unknown"
