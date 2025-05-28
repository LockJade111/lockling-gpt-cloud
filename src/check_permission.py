# src/check_permission.py

# 示例密钥数据库（可替换为数据库查询）
PERSONA_SECRETS = {
    "将军": "玉衡在手"
}

# 验证密钥是否匹配
def check_secret_permission(intent, persona, secret):
    expected = PERSONA_SECRETS.get(persona)
    return expected is not None and expected == secret

# 单独验证密钥（用于 register 时授权）
def check_persona_secret(persona, secret):
    expected = PERSONA_SECRETS.get(persona)
    return expected is not None and expected == secret
