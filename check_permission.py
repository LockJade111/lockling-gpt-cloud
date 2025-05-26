import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# ========== 常量读取 ==========
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "玉衡在手")

# 可选专属密钥映射（用于角色独立密钥）
PERSONA_SECRET_KEY_MAP = {
    "锁灵": "LOCKLING_SECRET",
    "军师猫": "STRATEGIST_SECRET",
    "司铃": "SECRETARY_SECRET",
    "玉衡": "SUPER_SECRET_KEY",
}

# Supabase 请求头
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ========== 函数区 ==========
def check_secret_permission(intent: str, persona: str, secret: str) -> bool:
    """
    三层权限验证机制：
    1. 超级密钥放行
    2. 专属环境变量匹配
    3. 从 Supabase personas 表中读取 bcrypt hash 对比密钥
    4. 然后检查 persona_roles 表是否授权了 intent

    返回 True 表示通过，False 表示拒绝
    """
    try:
        # ---------- 1. 超级密钥直接放行 ----------
        if secret == SUPER_SECRET_KEY:
            return True

        # ---------- 2. 专属角色密钥（如 LOCKLING_SECRET） ----------
        env_key_name = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key_name:
            env_secret = os.getenv(env_key_name)
            if env_secret and secret == env_secret:
                return True

        # ---------- 3. 从 Supabase 读取 bcrypt hash 匹配 ----------
        hash_url = f"{SUPABASE_URL}/rest/v1/persona_keys?persona=eq.{persona}&select=secret"
        res = requests.get(hash_url, headers=headers)

        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            if hashed and bcrypt.checkpw(secret.encode(), hashed.encode()):
                return is_intent_authorized(persona, intent)
        
        return False

    except Exception as e:
        print("❌ 权限校验失败:", e)
        return False


def is_intent_authorized(persona: str, intent: str) -> bool:
    """
    查询 persona_roles 表，是否该 persona 拥有 intent 权限
    """
    try:
        query_url = f"{SUPABASE_URL}/rest/v1/persona_roles?persona=eq.{persona}&intent=eq.{intent}"
        res = requests.get(query_url, headers=headers)

        if res.status_code == 200 and res.json():
            return True
        return False

    except Exception as e:
        print("❌ 权限验证失败:", e)
        return False
