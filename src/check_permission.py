# ✅ 动态密钥数据库
DYNAMIC_PERSONA_SECRETS = {
    "将军": "玉衡在手"
}

# ✅ 验证密钥是否匹配（用于登录确认）
def check_secret_permission(intent, persona, secret):
    expected = DYNAMIC_PERSONA_SECRETS.get(persona)
    return expected is not None and expected == secret

# ✅ 验证密钥是否正确（用于授权等只校验密钥的情况）
def check_persona_secret(persona, secret):
    expected = DYNAMIC_PERSONA_SECRETS.get(persona)
    return expected is not None and expected == secret

# ✅ 修改密钥（用于 intent_type == update_secret）
def update_persona_secret(persona, new_secret):
    DYNAMIC_PERSONA_SECRETS[persona] = new_secret
