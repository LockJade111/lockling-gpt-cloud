import os

# ✅ Persona → 环境变量 key 映射表（所有密钥统一英文变量名）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    # 可继续扩展其他角色
}

def check_secret_permission(persona: str, secret: str) -> bool:
    """
    核心密钥验证函数：
    - 将 persona 转换为合法的环境变量 key
    - 比对用户口令是否与系统记录一致
    """
    env_key = PERSONA_SECRET_KEY_MAP.get(persona)

    if not env_key:
        print(f"[❌] 密钥验证失败：未知 persona：{persona}")
        return False

    stored = os.getenv(env_key)
    print(f"[🔐] 密钥验证：persona={persona}，输入密钥={secret}，系统密钥={stored}")

    return stored == secret
