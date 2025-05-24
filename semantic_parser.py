# semantic_parser.py

def parse_intent(message: str):
    # 非常简单的规则示例，可以根据需要完善
    if "授权" in message and "注册" in message:
        return {
            "intent": "confirm_identity",
            "intent_type": "confirm_identity"
        }
    elif "注册角色" in message:
        return {
            "intent": "register_persona",
            "intent_type": "register_persona",
            "new_name": message.split("注册角色")[-1].strip()
        }
    elif "取消授权" in message:
        return {
            "intent": "revoke_identity",
            "intent_type": "revoke_identity"
        }
    elif "口令是" in message:
        return {
            "intent": "confirm_secret",
            "intent_type": "confirm_secret",
            "secret": message.split("口令是")[-1].strip()
        }
    else:
        return {
            "intent": "unknown",
            "intent_type": "unknown"
        }
