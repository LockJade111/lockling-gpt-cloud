# semantic_parser.py
import re
import openai

openai.api_key = "你的GPT-API-KEY"  # 或从环境变量加载更安全

# 主函数：由主逻辑调用
def parse_intent(message, persona):
    # 优先尝试 GPT 理解
    intent = try_gpt_parse(message, persona)
    if intent["intent_type"] != "unknown":
        return intent

    # GPT失败再走正则兜底
    return try_regex_parse(message, persona)


# ========== GPT解析模块 ==========
def try_gpt_parse(message, persona):
    try:
        prompt = f"""你是一个语义识别助手，请从下列句子中提取意图结构。输出JSON格式，字段包括：
- intent_type（如：register_persona、confirm_identity、revoke_identity、unknown）
- new_name（如是注册请求）
- identity（如是口令验证）
- target（如是授权/撤销谁）
- requires（如是赋予权限）
- source（原始消息）

句子如下：
「{message}」
说话人是：{persona}

请用英文JSON结构体返回，不加说明。
"""
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 可换成你的GPT版本
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        response = completion.choices[0].message.content.strip()
        return eval(response)  # 或用 json.loads(response) 更安全
    except Exception as e:
        return {
            "intent": "unknown",
            "intent_type": "unknown",
            "source": message,
            "persona": persona,
            "error": f"GPT解析异常：{str(e)}"
        }


# ========== 正则兜底模块 ==========
def try_regex_parse(message, persona):
    if "注册角色" in message:
        match = re.search(r"注册角色\s*(\S+)", message)
        if match:
            return {
                "intent": "register_persona",
                "intent_type": "register_persona",
                "new_name": match.group(1),
                "source": message,
                "persona": persona
            }

    if "授权" in message and "注册" in message:
        match = re.search(r"授权(\S+)[可以]*注册.*口令是(\S+)", message)
        if match:
            return {
                "intent": "confirm_identity",
                "intent_type": "confirm_identity",
                "target": match.group(1),
                "secret": match.group(2),
                "requires": "register_persona",
                "source": message,
                "persona": persona
            }

    if "取消" in message and "权限" in message:
        match = re.search(r"取消(\S+)注册权限", message)
        if match:
            return {
                "intent": "revoke_identity",
                "intent_type": "revoke_identity",
                "target": match.group(1),
                "requires": "register_persona",
                "source": message,
                "persona": persona
            }

    return {
        "intent": "unknown",
        "intent_type": "unknown",
        "source": message,
        "persona": persona
    }
