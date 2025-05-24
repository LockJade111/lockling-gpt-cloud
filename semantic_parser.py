# semantic_parser.py

import os
import openai
import re
import json

# 设置 OpenAI API Key（请确保环境变量已配置）
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ GPT 智能解析
def gpt_parse(message: str) -> dict:
    system_prompt = """
你是一个语义解析助手，请将用户的自然语言指令解析为以下结构的标准 JSON：
{
  "intent": "...",           // 意图关键词
  "intent_type": "...",      // 意图类型
  "target": "...",           // 若为授权操作，目标对象是谁
  "new_name": "...",         // 若为注册，角色名称
  "secret": "...",           // 若包含口令
  "requires": "..."          // 所请求的权限（如 register_persona）
}
如果无法判断，请设置 intent_type 为 "unknown"。不要添加注释或多余语言。
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 如需更省资源可用 "gpt-3.5-turbo"
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

# ✅ 本地正则 fallback 解析器
def local_parse(message: str) -> dict:
    result = {
        "intent": "unknown",
        "intent_type": "unknown",
        "source": message
    }

    # 注册角色
    match_reg = re.search(r"(?:我要)?注册角色[：:\s]*([\u4e00-\u9fa5A-Za-z0-9]+)", message)
    if match_reg:
        result.update({
            "intent": "register_persona",
            "intent_type": "register_persona",
            "new_name": match_reg.group(1).strip()
        })
        return result

    # 授权角色（包含口令）
    match_auth = re.search(r"(?:我要)?授权([\u4e00-\u9fa5A-Za-z0-9]+).*(注册|创建).*?(口令是|口令为|口令[:：])(.+)", message)
    if match_auth:
        result.update({
            "intent": "confirm_identity",
            "intent_type": "confirm_identity",
            "target": match_auth.group(1).strip(),
            "secret": match_auth.group(4).strip(),
            "requires": "register_persona"
        })
        return result

    # 撤销权限
    match_revoke = re.search(r"(?:我要)?取消([\u4e00-\u9fa5A-Za-z0-9]+).*注册.*权限", message)
    if match_revoke:
        result.update({
            "intent": "revoke_identity",
            "intent_type": "revoke_identity",
            "target": match_revoke.group(1).strip()
        })
        return result

    return result

# ✅ 统一封装接口，兼容主逻辑 parse_intent(message, persona)
def parse_intent(message: str, persona: str) -> dict:
    # 优先 GPT
    parsed = gpt_parse(message)
    if not parsed or parsed.get("intent_type") == "unknown":
        parsed = local_parse(message)

    # 补全字段
    parsed.setdefault("intent", "unknown")
    parsed.setdefault("intent_type", "unknown")
    parsed["source"] = message
    parsed["persona"] = persona
    return parsed
