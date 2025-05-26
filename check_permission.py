import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "玉衡在手")

# 可选映射：为特定 persona 提供专属密钥变量（可扩展）
PERSONA_SECRET_KEY_MAP = {
    "锁灵": "LOCKLING_SECRET",
    "军师猫": "STRATEGIST_SECRET",
    "司铃": "SECRETARY_SECRET",
    "玉衡": "SUPER_SECRET_KEY",
}

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def check_secret_permission(intent: str, persona: str, secret: str) -> bool:
    """
    校验传入密钥是否具备访问权限：

    1. 若是超级密钥，放行；
    2. 若 persona 有专属密钥，比较是否匹配；
    3. 否则从 Supabase personas 表中获取 bcrypt hash 校验。
    """
    try:
        # ✅ 超级密钥放行
        if secret == SUPER_SECRET_KEY:
            return True

        # ✅ 支持专属环境变量密钥（如 LOCKLING_SECRET）
        env_key_name = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key_name:
            env_secret = os.getenv(env_key_name)
            if env_secret and secret == env_secret:
                return True

        # ✅ 查询 Supabase personas 表（带 bcrypt 加密）
        url = f"{SUPABASE_URL}/rest/v1/personas?persona=eq.{persona}&select=secret"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("❌ Supabase 查询失败:", res.status_code)
            return False

        data = res.json()
        if not data:
            print("❌ persona 未找到:", persona)
            return False

        stored_hash = data[0].get("secret")
        if not stored_hash:
            print("❌ persona 未设置密钥:", persona)
            return False

        # ✅ bcrypt 校验密码
        return bcrypt.checkpw(secret.encode("utf-8"), stored_hash.encode("utf-8"))

    except Exception as e:
        print("❌ 权限验证失败:", e)
        return False
