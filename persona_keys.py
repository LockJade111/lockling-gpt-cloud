import bcrypt
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = "persona_keys"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 注册 persona（支持写入角色，返回布尔值 + 消息）
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
    # 查重
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
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"

# 验证 persona 密钥（含失败计数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
    try:
        result = supabase.table(TABLE).select("*").eq("persona", persona).execute()
        if not result.data:
            return False

        row = result.data[0]
        if row.get("locked"):
            return False

        hashed = row.get("secret_hash", "").encode()
        if bcrypt.checkpw(input_secret.encode(), hashed):
            # 清除失败计数
            supabase.table(TABLE).update({
                "failed_attempts": 0,
                "locked": False
            }).eq("persona", persona).execute()
            return True
        else:
            # 增加失败计数
            new_fail_count = row.get("failed_attempts", 0) + 1
            update_data = {
                "failed_attempts": new_fail_count
            }
            if new_fail_count >= 5:
                update_data["locked"] = True
            supabase.table(TABLE).update(update_data).eq("persona", persona).execute()
            return False
    except Exception:
        return False
# 软删除 persona：仅清空权限
def delete_persona(persona: str) -> str:
    try:
        result = supabase.table("roles").update({"permissions": []}).eq("role", persona).execute()
        if result.data:
            return f"🟡 角色 {persona} 的权限已清空（软删除）"
        else:
            return f"⚠️ 未找到角色 {persona}，未执行任何修改"
    except Exception as e:
        return f"❌ 删除失败：{str(e)}"

# 彻底删除 persona：从数据库中移除记录
def delete_persona_completely(persona: str) -> str:
    try:
        result = supabase.table("roles").delete().eq("role", persona).execute()
        if result.data:
            return f"🟥 角色 {persona} 已彻底删除（包含权限记录）"
        else:
            return f"⚠️ 未找到角色 {persona}，无删除动作"
    except Exception as e:
        return f"❌ 彻底删除失败：{str(e)}"
