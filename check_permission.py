import os
from persona_keys import check_persona_secret  # ✅ 数据库 bcrypt 哈希验证

# ✅ Persona → .env 环境变量名映射（用于本地密钥验证）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    "Lockling": "SUPER_SECRET_KEY",  # ✅ 默认管理密钥
    # ✅ 可继续拓展更多角色
}


def check_secret_permission(intent_or_persona, maybe_secret=None) -> bool:
    """
    ✅ 通用权限验证函数：
    支持两种调用方式：
    1. check_secret_permission(intent: dict, persona: str)
    2. check_secret_permission(persona: str, secret: str)
    """

    # === 模式 1：意图 + 角色身份验证（用于 GPT 推理阶段） ===
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_secret or ""

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        intent_type = intent.get("intent_type", "")
        high_risk_types = ["view_logs", "delete_persona", "revoke", "authorize"]

        if intent_type in high_risk_types:
            return persona == "将军"

        return True  # 默认放行

    # === 模式 2：角色 + 密钥验证（用于注册/删除） ===
    else:
        persona = intent_or_persona or ""
        secret = maybe_secret or ""

        # 1. 优先尝试本地环境变量口令校验
        expected_env_key = PERSONA_SECRET_KEY_MAP.get(persona)
        if expected_env_key:
            expected_secret = os.getenv(expected_env_key)
            if expected_secret and secret == expected_secret:
                return True

        # 2. 回退到数据库 bcrypt 密钥校验
        try:
            return check_persona_secret(supabase=None, persona=persona, secret=secret)
        except Exception:
            return False
