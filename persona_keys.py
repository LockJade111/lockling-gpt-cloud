import bcrypt
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = "persona_keys"

# ✅ 初始化 Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 注册 persona（旧接口写入 persona_keys）
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
    existing = supabase.table(TABLE).select("persona").eq("persona", persona).execute()
    if existing.data:
        return False, f"角色 {persona} 已存在"

    try:
        hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
        supabase.table(TABLE).insert({
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

# ✅ 密钥验证函数（带失败次数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
    try:
        result = supabase.table(TABLE).select("*").eq("persona", persona).execute()
        if not result.data:
            return False

        row = result.data[0]
        if row.get("locked"):
            return False

        if bcrypt.checkpw(input_secret.encode(), row["secret_hash"].encode()):
            # 成功后清零失败次数
            supabase.table(TABLE).update({"failed_attempts": 0}).eq("persona", persona).execute()
            return True
        else:
            # 密码错误增加失败次数
            attempts = row.get("failed_attempts", 0) + 1
            locked = attempts >= 5
            supabase.table(TABLE).update({
                "failed_attempts": attempts,
                "locked": locked
            }).eq("persona", persona).execute()
            return False
    except Exception as e:
        print(f"验证错误: {e}")
        return False

# ✅ 多表写入注册函数（注册 + 授权 + 日志）
def register_new_persona(persona: str, secret: str, operator="系统", permissions=[]):
    try:
        existing = supabase.table(TABLE).select("persona").eq("persona", persona).execute()
        if existing.data:
            return {"status": "fail", "message": f"角色 {persona} 已存在"}

        hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()

        # 1. persona_keys
        supabase.table("persona_keys").insert({
            "persona": persona,
            "secret_hash": hashed,
            "created_by": operator,
            "role": "user",
            "active": True,
            "failed_attempts": 0,
            "locked": False
        }).execute()

        # 2. personas
        supabase.table("personas").insert({
            "persona": persona,
            "title": "",
            "desc": "",
            "active": True
        }).execute()

        # 3. roles（仅当权限不为空）
        if permissions:
            supabase.table("roles").insert({
                "role": persona,
                "permissions": permissions,
                "active": True
            }).execute()

        # 4. logs
        supabase.table("logs").insert({
            "persona": operator,
            "intent_type": "register_persona",
            "target": persona,
            "allow": True,
            "result": f"注册成功权限{permissions}"
        }).execute()

        return {"status": "success", "message": "✅ 多表注册成功"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

import requests

def delete_persona(persona):
    """
    删除 persona_keysrolespersonas 三张表中该 persona 的记录
    """
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

    for table in ["persona_keys", "roles", "personas"]:
        url = f"{SUPABASE_URL}/rest/v1/{table}?persona=eq.{persona}"
        response = requests.delete(url, headers=headers)
        print(f"🗑️ 删除 {table} 中 persona={persona} 的记录{response.status_code}")

    return True
