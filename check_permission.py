# check_permission.py（开发模式通用允许）

def check_secret_permission(intent, persona, secret):
    return {
        "allow": True,
        "reason": "✅ 开发模式：默认允许所有操作",
        "persona": persona,
        "intent_type": intent.get("intent_type", "unknown")
    }
