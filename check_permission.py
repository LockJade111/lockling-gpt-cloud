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

        # 若传入 persona 为字典则提取名称
        if isinstance(persona, dict):
            persona = persona.get("name", "")

        intent_type = intent.get("intent_type", "")

        # 高风险意图：必须是将军才能执行
        high_risk_types = ["view_logs", "delete_persona", "revoke", "authorize"]

        if intent_type in high_risk_types:
            return persona == "将军"

        return True  # 其他指令默认放行

    # === 模式 2：角色 + 密钥验证（用于表单注册/删除） ===
    else:
        persona = intent_or_persona or ""
        secret = maybe_secret or ""

        if isinstance(persona, dict):
            persona = persona.get("name", "")

        if not persona or not secret:
            return False  # 缺失信息拒绝访问

        # ① 检查数据库哈希（推荐使用）
        if check_persona_secret(persona, secret):
            return True

        # ② 回退检查 .env 中的密钥匹配
        env_key_name = PERSONA_SECRET_KEY_MAP.get(persona)
        if env_key_name:
            expected_secret = os.getenv(env_key_name)
            return secret == expected_secret

        return False  # 默认拒绝
