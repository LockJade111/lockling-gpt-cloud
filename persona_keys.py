from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
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
        stored = data.get("secret")
        if stored and bcrypt.verify(secret, stored):
            return True, "密钥验证通过"
        else:
            return False, "密钥错误"
    except Exception as e:
        return False, str(e)

def update_permissions(persona, permissions):
    try:
        supabase.table("persona_keys").update({"permissions": permissions}).eq("persona", persona).execute()
        return True, "权限已更新"
    except Exception as e:
        return False, f"更新失败：{e}"

def get_all_personas():
    try:
        res = supabase.table("persona_keys").select("persona, permissions").execute()
        return res.data
    except Exception:
        return []

def delete_persona_completely(persona: str) -> tuple[bool, str]:
    try:
        supabase.table("persona_keys").delete().eq("persona", persona).execute()
        supabase.table("logs").delete().eq("persona", persona).execute()
        return True, f"角色 {persona} 及其日志记录已彻底清除"
    except Exception as e:
        return False, f"彻底删除失败：{e}"
