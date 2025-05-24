import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str):
    prompt = f"""
你是一个权限判断和语义解析引擎，负责将用户发出的自然语言指令转换为结构化意图。

现在系统中有不同的身份（persona），权限如下：

🟢 persona = "将军"
- 是系统最高权限持有者，拥有全部权限（包括注册、授权等）。
- 但必须提供正确的密钥才能执行任何敏感操作。
- 密钥通常会在语句中体现为 “口令是XXX” 或 “密钥是XXX”。

🟡 persona = 其他（如“司铃”、“军师猫”、“陌生人”）
- 默认无注册、授权等权限，需先被“将军”授权才可操作。

你的任务是从用户输入中识别以下字段：
1. intent_type（可选值：confirm_secret, register_persona, confirm_identity, unknown）
2. target（被注册或被授权的对象）
3. secret（如有提及口令）
4. allow（是否允许执行此行为，必须根据身份 + 密钥判断）
5. reason（GPT 的判断理由）

现在用户以 persona="{persona}" 的身份说：
“{message}”

请你判断他的真实意图，并根据上述身份权限逻辑返回结构化 JSON（严格格式）：
{{
  "intent_type": "...",
  "target": "...",
  "secret": "...",
  "allow": true/false,
  "reason": "..."
}}

⚠️ 重要说明：
- 若 persona 是将军，且有密钥（如“玉衡在手”），则可 allow=true；
- 否则默认 allow=false，并说明原因（如：未提供密钥、身份权限不足）；
- 不要生成代码、注释、解释或非 JSON 格式内容。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)
        result["persona"] = persona
        result["source"] = message
        return result

    except Exception as e:
        return {
            "intent_type": "unknown",
            "persona": persona,
            "source": message,
            "allow": False,
            "reason": f"⚠️ GPT响应失败：{str(e)}"
        }
