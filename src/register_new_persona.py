import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def hash_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()

def register_new_persona(persona: str, secret: str, name: str = "", role: str = "", tone: str = "", intro: str = "", authorize: str = ""):
    """
    向三张表写入新角色信息（persona_keys, personas, roles）
    仅当 authorize 不为空时才写入 roles
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "error", "message": "未配置 Supabase 环境变量"}

    try:
        # Step 1: persona_keys（身份与密钥）
        secret_hash = hash_secret(secret)
        keys_payload = {
            "persona": persona,
            "secret_hash": secret_hash,
            "role": role or "user",
            "active": True,
            "created_by": "系统",
            "intro": intro or f"{name or persona} 的智能体"
        }
        r1 = requests.post(f"{SUPABASE_URL}/rest/v1/persona_keys", headers=headers, json=keys_payload)
        if not r1.ok:
            return {"status": "error", "step": "persona_keys", "message": r1.text}

        # Step 2: personas（角色描述）
            "persona": persona,
    "name": name or persona,
    "role": personas_payload = {
            "persona": persona,
            "name": name or persona,
            "role": role or "智能角色",
            "tone": tone or "稳重",
            "intro": intro or f"{name or persona} 的智能角色"
        }
        r2 = requests.post(f"{SUPABASE_URL}/rest/v1/personas", headers=headers, json=personas_payload)
        if not r2.ok:
            return {"status": "error", "step": "personas", "message": r2.text}
        
        # Step 3: roles（授权权限，仅当指定了授权对象时写入）
        if authorize:   
            roles_payload = {  
                "source": persona,
                "target": authorize,
                "granted_by": "系统"
            }
            r3 = requests.post(f"{SUPABASE_URL}/rest/v1/roles", headers=headers, json=roles_payload)  
            if not r3.ok:
                return {"status": "error", "step": "roles", "message": r3.text}
        
        # Step 4: 返回成功
        return {"status": "success", "message": f"角色 {persona} 注册成功"}
        
    except Exception as e:  
        return {"status": "error", "message": str(e)}
