import os
import bcrypt

# ✅ 本地环境变量密钥映射
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    "Lockling": "SUPER_SECRET_KEY",
    # ⬇️ 可拓展更多授权角色
}

# ✅ 数据库哈希校验函数（临时内置，正式部署时建议移入 persona_keys.py）
# 模拟从数据库取出 hashed 密钥（请替换为你实际的查询函数）
def get_hashed_secret_from_db(persona: str) -> str:
    mock_db = {
        "将军": "$2b$12$abcdefghijk1234567890uvwxYzABCDEabcdeFgHiJKLmNOpQR",  # 伪数据
        "司铃": "$2b$12$klmnopqrstu1234567890vwxyZABCDEabcdeFgHiJKLmNOpQR",  # 伪数据
    }
    return mock_db.get(persona, "")

def check_persona_secret(persona: str, input_secret: str) -> bool:
    hashed = get_hashed_secret_from_db(persona)
    if not hashed:
        return False
    return bcrypt.checkpw(input_secret.encode("utf-8"), hashed.encode("utf-8"))


def check_secret_permission(intent_or_persona, maybe_secret=None) -> bool:
    """
    ✅ 通用权限验证函数：
    两种调用模式：
    1. check_secret_permission(intent: dict, persona: str)
       ✅ 用于 GPT 执行意图前的权限判断
    2. check_secret_permission(persona: str, secret: str)
       ✅ 用于注册、删除、授权等操作时校验密钥
    """
    # === 模式 1：GPT 意图执行权限判断 ===
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_secret or ""

        # 若 persona 是 dict 格式（来自前端 JSON）
        if isinstance(persona, dict):
            persona = persona.get("name", "")

        intent_type = intent.get("intent_type", "")
        high_risk_intents = ["view_logs", "delete_persona", "revoke", "authorize"]

        if intent_type in high_risk_intents:
            return persona == "将军"  # 仅将军可执行高权限意图

        return True  # 默认放行其他意图

    # === 模式 2：注册/删除/授权等密钥验证 ===
    else:
        persona = intent_or_persona or ""
        secret = maybe_secret or ""

        # 1. 优先校验环境变量
        env_key = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key:
            expected = os.getenv(env_key)
            if expected and expected == secret:
                return True

        # 2. 如果环境变量不通过，尝试数据库哈希验证
        return check_persona_secret(persona, secret)
