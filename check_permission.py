import os
from persona_keys import check_persona_secret  # 数据库密钥验证函数

# ✅ Persona → 环境变量 key 映射（变量名使用英文，不含中文）
PERSONA_SECRET_KEY_MAP = {
    "将军": "SECRET_COMMANDER",
    "司铃": "SECRET_ASSISTANT",
    "军师猫": "SECRET_STRATEGIST",
    # 🧩 若新增角色，请在此处同步维护 KEY 映射关系
}

def check_secret_permission(persona: str, secret: str) -> bool:
    """
    混合验证机制：
    1. 优先使用 Supabase 数据库中的 bcrypt 哈希验证（安全）；
    2. 若数据库中不存在或验证失败，则回退至 .env 明文对比（兜底机制）；
    3. 匹配失败则统一返回 False。
    """
    # ✅ Step 1：数据库验证
    if check_persona_secret(persona, secret):
        print(f"[✅] 数据库验证成功：persona={persona}")
        return True

    # ✅ Step 2：本地环境变量兜底验证
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

# ✅ 查询日志权限判断（将军专属）
def has_log_access(persona: str) -> bool:
    """
    限定仅特定 persona（如“将军”）可访问系统日志接口。
    """
    return persona.strip() == "将军"
