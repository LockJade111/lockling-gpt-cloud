# semantic_parser.py
import re
import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(message, persona):
    # 优先尝试 GPT 理解
    intent = try_gpt_parse(message, persona)
    if intent.get("intent_type") != "unknown":
        return intent

    # 如果GPT失败走正则解析兜底
    return try_regex_parse(message, persona)


# ========== GPT解析模块 ==========
def try_gpt_parse(message, persona):
    try:
        prompt = f"""
你是一个语义理解助手请根据下方输入内容提取操作意图并以 JSON 结构返回（不要任何注释或解释）

字段包括
- intent英文动作（如 register_persona、confirm_identity、revoke_identity）
- intent_type同 intent（可重复）
- new_name如是注册角色
- identity如包含口令
- target如涉及对象（被授权/撤权者）
- requires如赋予的权限关键字
- source原始语句
- persona说话人身份

输入
「{message}」
说话人是{persona}

输出JSON
"""

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        response = completion.choices[0].message.content.strip()
        data = json.loads(response)

        # 确保必要字段存在
        data.setdefault("intent", "unknown")
        data.setdefault("intent_type", "unknown")
        data.setdefault("source", message)
        data.setdefault("persona", persona)

        return data

    except Exception as e:
        return {
            "intent": "unknown",
            "intent_type": "unknown",
            "source": message,
            "persona": persona,
        }


# ========== 正则兜底解析 ==========
def try_regex_parse(message, persona):
    result = {
        "intent": "unknown",
        "intent_type": "unknown",
        "source": message,
        "persona": persona,
    }

    # 注册角色
    if re.search(r"注册角色", message):
        match = re.search(r"注册角色\s*(\S+)", message)
        if match:
            new_name = match.group(1)
            result.update({
                "intent": "register_persona",
                "intent_type": "register_persona",
                "new_name": new_name
            })

    # 授权操作（带口令）
    elif re.search(r"授权\S+可以注册", message) and re.search(r"口令是", message):
        target_match = re.search(r"授权(\S+?)可以注册", message)
        secret_match = re.search(r"口令是(\S+)", message)
        if target_match and secret_match:
            result.update({
                "intent": "confirm_identity",
                "intent_type": "confirm_identity",
                "target": target_match.group(1),
                "secret": secret_match.group(1),
                "requires": "register_persona"
            })

    # 取消授权
    elif re.search(r"取消(\S+)注册权限", message):
        target = re.search(r"取消(\S+)注册权限", message).group(1)
        result.update({
            "intent": "revoke_identity",
            "intent_type": "revoke_identity",
            "target": target,
            "requires": "register_persona"
        })

    # 单独识别口令
    elif re.search(r"口令是\s*(\S+)", message):
        result.update({
            "intent": "confirm_secret",
            "intent_type": "confirm_secret",
            "secret": re.search(r"口令是\s*(\S+)", message).group(1)
        })

    return result
