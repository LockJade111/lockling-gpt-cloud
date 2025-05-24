import os
from persona_keys import check_persona_secret  # 数据库密钥验证函数

# ✅ Persona → 环境变量 key 映射（变量名使用英文，不含中文）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    # 可继续扩展其他角色
}

def check_secret_permission(persona: str, secret: str) -> bool:
    """
    混合验证机制：
    1. 优先使用数据库中的 bcrypt 哈希验证（安全）
    2. 若数据库中不存在或出错，回退至 .env 明文验证（兜底）
    """
    # ✅ 先查数据库密钥
    if check_persona_secret(persona, secret):
        print(f"[✅] 数据库验证成功：persona={persona}")
        return True

    # ❗若数据库验证失败，退回本地 .env
    env_key = PERSONA_SECRET_KEY_MAP.get(persona)
    if not env_key:
        print(f"[❌] 验证失败：未知 persona：{persona}")
        return False

    stored = os.getenv(env_key)
    if stored == secret:
        print(f"[✅] 本地密钥匹配成功：persona={persona}")
        return True
    else:
        print(f"[❌] 本地密钥匹配失败：输入={secret}，系统={stored}")
        return False
