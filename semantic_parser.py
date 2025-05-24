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
            model="gpt-4",  # 可替换为 gpt-3.5-turbo
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

# ✅ 本地备用解析器（fallback 正则规则）
def local_parse(message: str) -> dict:
    # 授权指令（包含“授权”、“允许”，和“口令”）
    if re.search(r"(授权|允许).+(注册|创建).+口令", message):
        target_match = re.search(r"(?:授权|允许)(.*?)可以", message)
        secret_match = re.search(r"口令(是|为)?(.+)", message)
        if target_match and secret_match:
            return {
                "intent": "confirm_secret",
                "intent_type": "confirm_secret",
                "target": target_match.group(1).strip(),
                "secret": secret_match.group(2).strip()
            }

    # 注册角色（如：“我要注册角色 小助手”）
    if re.search(r"(我要)?注册(新)?角色", message):
        name_match = re.search(r"角色[：:\s]?(.+)", message)
        if name_match:
            return {
                "intent": "register_persona",
                "intent_type": "register_persona",
                "new_name": name_match.group(1).strip()
            }

    # 撤销权限（如：“我要取消司铃注册权限”）
    if "取消" in message and "权限" in message:
        target_match = re.search(r"取消(.*?)权限", message)
        if target_match:
            return {
                "intent": "revoke_identity",
                "intent_type": "revoke_identity",
                "target": target_match.group(1).strip()
            }

    # 未识别成功
    return {
        "intent": "unknown",
        "intent_type": "unknown"
    }

# ✅ 顶层调用接口
def parse_intent(message: str) -> dict:
    parsed = gpt_parse(message)
    if parsed and parsed.get("intent_type") != "unknown":
        return parsed
    else:
        print("⚠️ GPT未能成功解析，启用本地规则")
        return local_parse(message)
