import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "玉衡在手")

# 可选：为每个 persona 指定专属密钥环境变量（如：LOCKLING_SECRET）
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


def check_persona_secret(persona: str, secret: str) -> bool:
    """
    从 Supabase 的 personas 表中查询该 persona 的 hashed 密码并验证。
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/personas?persona=eq.{persona}&select=secret"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return False

        data = response.json()
        if not data:
            return False

        hashed = data[0].get("secret")
        if not hashed:
            return False

        return bcrypt.checkpw(secret.encode("utf-8"), hashed.encode("utf-8"))

    except Exception as e:
        print("❌ check_persona_secret 异常：", e)
        return False


def check_secret_permission(intent_or_persona, maybe_persona=None, maybe_secret=None):
    """
    兼容两种调用方式：
    - 聊天 intent 模式：check_secret_permission(intent, persona, secret)
    - 注册/删除/授权模式：check_secret_permission(persona, secret)
    """
    # === 模式 1：高权限意图校验 ===
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_persona or ""
        secret = maybe_secret or ""
        intent_type = intent.get("intent_type", "")
        high_risk_intents = ["view_logs", "delete_persona", "revoke", "authorize"]

        if intent_type in high_risk_intents:
            return persona == "将军"  # 只有“将军”角色能执行高权限意图
        return True  # 其他意图默认放行

    # === 模式 2：密钥权限注册类操作 ===
    else:
        persona = intent_or_persona or ""
        secret = maybe_persona or ""

        # 1. 超级密钥全通行
        if secret == SUPER_SECRET_KEY:
            return True

        # 2. 环境变量密钥
        env_var = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_var:
            expected = os.getenv(env_var)
            if expected and expected == secret:
                return True

        # 3. 数据库 bcrypt 密钥验证
        return check_persona_secret(persona, secret)
