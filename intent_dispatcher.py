from persona_keys import (
    check_secret,
    register_persona,
    update_permissions,
    delete_persona_completely,
)

def dispatcher(intent):
    try:
        intent_type = intent.get("intent_type")
        persona = intent.get("persona")
        target = intent.get("target")

        if intent_type == "confirm_secret":
            secret = intent.get("secret")
            success, msg = check_secret(persona, secret)
            return {"success": success, "message": msg}

        elif intent_type == "register_persona":
            secret = intent.get("secret")
            success, msg = register_persona(target, secret)
            return {"success": success, "message": msg}

        elif intent_type == "update_permissions":
            perms = intent.get("permissions", [])
            success, msg = update_permissions(target, perms)
            return {"success": success, "message": msg}

        elif intent_type == "delete_persona_full":
            success, msg = delete_persona_completely(target)
            return {"success": success, "message": msg}

        else:
            return {"success": False, "message": f"未知意图类型：{intent_type}"}
    except Exception as e:
        return {"success": False, "message": f"Dispatcher 错误：{str(e)}"}
