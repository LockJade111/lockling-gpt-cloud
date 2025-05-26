import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def register_new_persona(persona: str, secret: str, name: str = "", role: str = "", tone: str = "", prompt: str = ""):
    """
    向三张表写入新角色信息（persona_keys, roles, personas）
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "error", "message": "未配置 Supabase 环境变量"}

    try:
        # 👁‍🗨 1. 添加 persona_keys（身份验证用）
        keys_payload = {
            "persona": persona,
            "secret_hash": secret,
            "role": "user",
            "active": True,
            "created_by": "系统"
        }
        r1 = requests.post(f"{SUPABASE_URL}/persona_keys", headers=headers, json=keys_payload)
        if not r1.ok:
            return {"status": "error", "step": "persona_keys", "message": r1.text}

        # 🛡 2. 添加 roles（授权权限用）
        roles_payload = {
            "persona": persona,
            "permissions": [],  # 后续再授权
            "granted_by": "系统"
        }
        r2 = requests.post(f"{SUPABASE_URL}/roles", headers=headers, json=roles_payload)
        if not r2.ok:
            return {"status": "error", "step": "roles", "message": r2.text}

        # 🎭 3. 添加 personas（角色定义与个性描述）
        personas_payload = {
            "persona": persona,
            "name": name,
            "role": role,
            "tone": tone,
            "prompt": prompt,
            "age": None,
            "gender": None
        }
        r3 = requests.post(f"{SUPABASE_URL}/personas", headers=headers, json=personas_payload)
        if not r3.ok:
            return {"status": "error", "step": "personas", "message": r3.text}

        return {"status": "success", "message": "注册成功"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
