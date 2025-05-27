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

# ✅ 核心权限函数（返回结构化权限结果）
def check_secret_permission(intent: dict, persona: str, secret: str) -> dict:
    """
    权限验证机制（四层）：
    1. 超级密钥立即放行
    2. 专属环境密钥比对
    3. Supabase bcrypt 密钥验证
    4. persona_roles 表中 intent 权限比对

    返回结构：
    {
        "allow": True / False,
        "reason": "...",
        "persona": "小艾",
        "intent_type": "authorize"
    }
    """
    try:
        # 预处理字段
        intent_type = intent.get("intent_type", "unknown")
        result = {
            "allow": False,
            "reason": "❌ 默认拒绝，未通过任一验证路径",
            "persona": persona,
            "intent_type": intent_type
        }

        # ---------- 1. 超级密钥直接放行 ----------
        if secret == SUPER_SECRET_KEY:
            result["allow"] = True
            result["reason"] = "✅ 超级密钥授权"
            return result

        # ---------- 2. 专属角色密钥匹配 ----------
        env_key_name = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key_name:
            env_secret = os.getenv(env_key_name)
            if env_secret and secret == env_secret:
                result["allow"] = True
                result["reason"] = f"✅ {persona} 的专属密钥通过验证"
                return result

        # ---------- 3. bcrypt hash 比对 ----------
        hash_url = f"{SUPABASE_URL}/rest/v1/persona_keys?persona=eq.{persona}&select=secret"
        res = requests.get(hash_url, headers=headers)
        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            if hashed and bcrypt.checkpw(secret.encode(), hashed.encode()):
                # ---------- 4. 检查 intent 权限 ----------
                if is_intent_authorized(persona, intent_type):
                    result["allow"] = True
                    result["reason"] = f"✅ 密钥正确且具有权限：{intent_type}"
                else:
                    result["reason"] = f"❌ 密钥正确，但无权执行：{intent_type}"
                return result

        # 所有验证失败
        result["reason"] = "❌ 密钥验证失败或权限未授权"
        return result

    except Exception as e:
        print("❌ 权限校验异常:", e)
        return {
            "allow": False,
            "reason": f"❌ 异常错误：{str(e)}",
            "persona": persona,
            "intent_type": intent.get("intent_type", "unknown")
        }

# ✅ 权限表比对
def is_intent_authorized(persona: str, intent: str) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/persona_roles?persona=eq.{persona}&intent=eq.{intent}"
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json():
            return True
        return False
    except Exception as e:
        print("❌ intent 权限验证失败:", e)
        return False
