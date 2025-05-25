from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

from passlib.hash import bcrypt

def register_persona(persona, secret):
    try:
        hashed = bcrypt.hash(secret)
        supabase.table("persona_keys").insert({
            "persona": persona,
            "secret": hashed,
            "permissions": []
        }).execute()
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败：{e}"

def check_secret(persona, secret):
    try:
        data = supabase.table("persona_keys").select("*").eq("persona", persona).single().execute().data
        if not data:
            return False, "未找到该角色"
        if bcrypt.verify(secret, data.get("secret", "")):
            return True, "密钥正确"
        else:
            return False, "密钥错误"
    except Exception as e:
        return False, str(e)

def update_permissions(persona, permissions):
    try:
        supabase.table("persona_keys").update({"permissions": permissions}).eq("persona", persona).execute()
        return True, "权限更新成功"
    except Exception as e:
        return False, f"更新失败：{e}"

def delete_persona_soft(persona):
    try:
        supabase.table("persona_keys").update({"deleted": True}).eq("persona", persona).execute()
        return "🟡 角色软删除成功（已标记为 deleted=True）"
    except Exception as e:
        return f"❌ 软删除失败：{e}"

def delete_persona_completely(persona):
    try:
        supabase.table("persona_keys").delete().eq("persona", persona).execute()
        try:
            supabase.table("logs").delete().eq("persona", persona).execute()
        except Exception as e:
            print("[⚠️ 日志删除失败]", e)
        return "✅ 角色与日志已彻底删除"
    except Exception as e:
        return f"❌ 彻底删除失败：{e}"
