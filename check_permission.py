import os
from persona_keys import check_persona_secret  # 数据库 bcrypt 哈希验证

# ✅ Persona → .env 环境变量名映射（用于本地密钥验证）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    # 后续角色在此新增映射
}

def check_secret_permission(intent_or_persona, maybe_secret=None) -> bool:
    """
    ✅ 通用权限验证函数：
    支持以下调用方式：
    - check_secret_permission(intent, persona_dict or str)
    - check_secret_permission(persona, secret)
    """
    # 若传入为 intent + persona 格式
    if isinstance(intent_or_persona, dict):
        intent = intent_or_persona
        persona = maybe_secret

        # 容错处理：若 persona 是 dict，从中提取 name
        if isinstance(persona, dict):
            persona = persona.get("name", "")

        # 若 intent 中标记 intent_type 受限，仅限将军
        intent_type = intent.get("intent_type", "")
        if intent_type in ["view_logs", "delete_persona", "revoke", "authorize"]:
            return persona == "将军"
        return True  # 默认放行
    else:
        # persona + secret 验证模式
        persona = intent_or_persona
        secret = maybe_secret

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        # ✅ Step 1：数据库验证
        if check_persona_secret(persona, secret):
            print(f"[✅] 数据库验证成功：persona={persona}")
            return True

        # ✅ Step 2：本地 .env 验证
        env_key = PERSONA_SECRET_KEY_MAP.get(persona)
        if not env_key:
            print(f"[❌] 验证失败：未知 persona『{persona}』无对应环境变量 key")
            return False

        stored = os.getenv(env_key)
        if stored == secret:
            print(f"[✅] 本地密钥匹配成功：persona={persona}")
            return True
        else:
            print(f"[❌] 本地密钥匹配失败：persona={persona}，输入={secret}，预期={stored}")
            return False

# ✅ 限制将军查看日志页面
def has_log_access(persona) -> bool:
    if isinstance(persona, dict):
        persona = persona.get("name", "")
    return persona.strip() == "将军"
