import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str):
    prompt = f"""
你是一个权限与语义解析系统，负责将用户发出的自然语言命令，转换为结构化意图。

系统中有多种身份（persona），例如：
🟢 persona="将军"：系统最高权限者，可注册、授权、撤销、删除等敏感操作，需提供密钥（如“玉衡在手”）。
🟡 persona="司铃"、"小助手" 等：默认无注册/授权权限，需被“将军”授权后才可操作。

你需识别以下意图类型（intent_type）：

1. confirm_secret       → 身份验证，如 “口令是玉衡在手”
2. register_persona     → 注册角色，如 “我要注册角色 小助手”
3. confirm_identity     → 授权他人，如 “我要授权 司铃 注册权限”
4. revoke_identity      → 取消授权，如 “我要取消 司铃 的注册权限”
5. delete_persona       → 删除角色，如 “我要删除角色 小助手”
6. unknown              → 其他无法识别或无权限的内容

---

【示例】：

- “口令是玉衡在手” → confirm_secret
- “我要注册角色 小助手，口令是玉衡在手” → register_persona
- “我要授权 司铃 可以注册角色，口令是玉衡在手” → confirm_identity
- “我要取消 司铃 的注册权限，口令是玉衡在手” → revoke_identity
- “我要删除角色 小助手，口令是玉衡在手” → delete_persona
- “你好” → unknown

---

【输出格式要求（仅 JSON，无注释）】：

{{
  "intent_type": "...",
  "target": "...",
  "secret": "...",
  "allow": true/false,
  "reason": "..."
}}

请你基于 persona="{persona}" 与消息：
“{message}”
判断指令并返回 JSON。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
        result["persona"] = persona
        result["source"] = message
        return result

    except Exception as e:
        return {
            "intent_type": "unknown",
            "target": None,
            "secret": "",
            "allow": False,
            "reason": f"⚠️ GPT解析失败：{str(e)}",
            "persona": persona,
            "source": message
        }
