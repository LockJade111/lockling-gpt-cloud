# semantic_parser.py

def parse_intent(message: str) -> dict:
    """
    基于关键词的意图解析器
    返回包含 intent_type 及相关字段的字典
    """
    message = message.strip()
    result = {
        "intent": "unknown",
        "intent_type": "unknown"
    }

    # ✅ 授权 + 口令型（授权指令+口令必须优先判断）
    if "授权" in message and "口令是" in message:
        result["intent"] = "confirm_secret"
        result["intent_type"] = "confirm_secret"
        result["secret"] = message.split("口令是")[-1].strip()

    # ✅ 授权身份（授权谁可以注册）
    elif "授权" in message and "注册" in message:
        result["intent"] = "confirm_identity"
        result["intent_type"] = "confirm_identity"
        # 尝试提取目标角色
        for name in ["司铃", "军师猫", "小助手"]:
            if name in message:
                result["target"] = name

    # ✅ 注册角色
    elif "注册角色" in message:
        result["intent"] = "register_persona"
        result["intent_type"] = "register_persona"
        result["new_name"] = message.split("注册角色")[-1].strip()

    # ✅ 取消授权
    elif "取消" in message and "授权" in message:
        result["intent"] = "revoke_identity"
        result["intent_type"] = "revoke_identity"
        # 尝试提取目标
        for name in ["司铃", "军师猫", "小助手"]:
            if name in message:
                result["target"] = name

    # ✅ 兜底返回
    return result
