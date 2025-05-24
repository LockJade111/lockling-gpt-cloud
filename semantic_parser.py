# semantic_parser.py

import os
import openai
import re
import json

# 设置 OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


# ✅ GPT 智能语义解析器
def gpt_parse(message: str) -> dict:
    system_prompt = """
你是一个语义解析助手，请将用户的自然语言指令解析为以下结构的标准 JSON：
{
  "intent": "...",           // 意图关键词
  "intent_type": "...",      // 意图类型
  "target": "...",           // 若为授权操作，目标对象是谁
  "new_name": "...",         // 若为注册，角色名称
  "secret": "...",           // 若包含口令
  "requires": "..."          // 所请求的权限（如注册 register_persona）
}
如果无法判断，请设置 intent_type 为 "unknown"。不要添加注释或多余语言。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 可替换为 "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"⚠️ GPT解析失败：{e}")
        return None


# ✅ 本地备用解析器（正则规则）
def local_parse(message: str) -> dict:
    message = message.strip()
    intent = {"intent": "unknown", "intent_type": "unknown"}

    if "注册角色" in message:
        match = re.search(r"注册角色[\s]*([^\s，。]+)", message)
        if match:
            intent.update({
                "intent": "register_persona",
                "intent_type": "register_persona",
                "new_name": match.group(1),
                "source": message
            })
    elif "授权" in message and "注册角色" in message:
        match = re.search(r"授权([\u4e00-\u9fa5A-Za-z0-9_]+).*注册角色", message)
        secret_match = re.search(r"口令是([\u4e00-\u9fa5A-Za-z0-9_]+)", message)
        if match:
            intent.update({
                "intent": "confirm_identity",
                "intent_type": "confirm_identity",
                "target": match.group(1),
                "secret": secret_match.group(1) if secret_match else "",
                "source": message
            })
    elif "取消" in message and "权限" in message:
        match = re.search(r"取消([\u4e00-\u9fa5A-Za-z0-9_]+).*权限", message)
        if match:
            intent.update({
                "intent": "revoke_identity",
                "intent_type": "revoke_identity",
                "target": match.group(1),
                "source": message
            })

    return intent


# ✅ 主入口：统一调用接口
def parse_intent(message: str, persona: str = None) -> dict:
    print(f"🧠 开始解析意图：message='{message}' | persona='{persona}'")
    intent = gpt_parse(message)

    if intent is None or intent.get("intent_type") == "unknown":
        print("🔁 尝试 fallback 到本地解析器...")
        intent = local_parse(message)

    if not isinstance(intent, dict):
        return {"intent": "unknown", "intent_type": "unknown"}
    
    # 加入 source 和 persona 补充字段
    intent.setdefault("source", message)
    intent.setdefault("persona", persona)
    return intent
