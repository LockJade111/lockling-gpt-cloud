# semantic_parser.py

import os
import openai

# 设置 API 密钥
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ GPT 智能解析器
def gpt_parse(message: str) -> dict:
    system_prompt = """
你是一个语义解析助手，请将用户的自然语言指令解析为以下结构：
{
  "intent_type": "...",
  "target": "...",        # 若有授权对象
  "new_name": "...",      # 若是注册角色
  "secret": "...",        # 若有口令
  "requires": "..."       # 系统权限，如 "register_persona"
}
如果无法识别意图，请设置 intent_type 为 "unknown"。
请确保返回内容为标准 JSON 格式，绝不添加注释或多余文本。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 可改为 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("{"):
            return eval(content)
        return {"intent_type": "unknown"}
    except Exception as e:
        print(f"⚠️ GPT解析失败：{e}")
        return None

# ✅ 本地备用解析器
def local_parse(message: str) -> dict:
    message = message.strip()
    result = {
        "intent": "unknown",
        "intent_type": "unknown"
    }

    if "授权" in message and "口令是" in message:
        result["intent"] = "confirm_secret"
        result["intent_type"] = "confirm_secret"
        result["secret"] = message.split("口令是")[-1].strip()

    elif "授权" in message and "注册" in message:
        result["intent"] = "confirm_identity"
        result["intent_type"] = "confirm_identity"
        for name in ["司铃", "军师猫", "小助手"]:
            if name in message:
                result["target"] = name
        result["requires"] = "register_persona"

    elif "注册角色" in message:
        result["intent"] = "register_persona"
        result["intent_type"] = "register_persona"
        result["new_name"] = message.split("注册角色")[-1].strip()
        result["requires"] = "register_persona"

    elif "取消" in message and "授权" in message:
        result["intent"] = "revoke_identity"
        result["intent_type"] = "revoke_identity"
        for name in ["司铃", "军师猫", "小助手"]:
            if name in message:
                result["target"] = name

    return result

# ✅ 自动调度：优先 GPT，失败则 fallback 本地
def parse_intent(message: str) -> dict:
    parsed = gpt_parse(message)
    if parsed:
        print("🧠 使用 GPT 解析成功")
        return parsed
    else:
        print("⚙️ 回退至本地解析")
        return local_parse(message)
