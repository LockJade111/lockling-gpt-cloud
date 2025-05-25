import os
from persona_keys import check_persona_secret  # ✅ 数据库 bcrypt 哈希验证

# ✅ Persona → .env 环境变量名映射（用于本地密钥验证）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    # 可拓展更多角色
}

def check_secret_permission(intent_or_persona, maybe_secret=None) -> bool:
    """
    ✅ 通用权限验证函数：
    支持以下两种调用方式：
    1. check_secret_permission(intent, persona)
    2. check_secret_permission(persona, secret)
    """

    # === 模式 1：intent + persona 结构 ===
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_secret

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        intent_type = intent.get("intent_type", "")

        # 限制命令：只有将军可执行
        if intent_type in ["view_logs", "delete_persona", "revoke", "authorize"]:
            return persona == "将军"

        return True  # 默认放行

    # === 模式 2：persona + secret 模式 ===
    else:
        persona = intent_or_persona
        secret = maybe_secret

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        # ✅ Step 1：数据库验证
        if check_persona_secret(persona, secret):
            print(f"[✅] 数据库验证成功：persona={persona}")
            return True

        # ✅ Step 2：本地环境变量验证
        env_key = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key:
            expected = os.getenv(env_key, "").strip()
            if expected and expected == secret:
                print(f"[✅] 环境变量验证成功：persona={persona}")
                return True

        print(f"[❌] 验证失败：persona={persona}")
        return False
