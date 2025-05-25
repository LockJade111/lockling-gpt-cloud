import os
from persona_keys import check_persona_secret  # ✅ 支持数据库中 bcrypt 校验

# ✅ Persona → .env 环境变量名映射（用于本地密钥验证）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    "Lockling": "SUPER_SECRET_KEY",  # ✅ 默认管理密钥
    # 可拓展更多角色
}

def check_secret_permission(intent_or_persona, maybe_secret=None) -> bool:
    """
    ✅ 通用权限验证函数：
    支持以下两种调用方式：
    1. check_secret_permission(intent, persona)
    2. check_secret_permission(persona, secret)
    """

    # === 模式 1：intent + persona ===
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_secret

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        intent_type = intent.get("intent_type", "")

        # 限制指令：仅“将军”可执行高级操作
        if intent_type in ["view_logs", "delete_persona", "revoke", "authorize"]:
            return persona == "将军"

        return True  # 其他指令默认放行

    # === 模式 2：persona + secret ===
    else:
        persona = intent_or_persona
        secret = maybe_secret

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        if not persona or not secret:
            return False  # 缺失参数直接拒绝

        # ✅ Step 1：数据库密码校验
        if check_persona_secret(persona, secret):
            return True

        # ✅ Step 2：本地 .env 密钥校验
        env_key_name = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key_name:
            expected_secret = os.getenv(env_key_name)
            if expected_secret and secret == expected_secret:
                return True

        return False  # 所有校验失败，权限拒绝
