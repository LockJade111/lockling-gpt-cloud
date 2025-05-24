import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")  # 确保 .env 中有此项

def parse_intent(message: str, persona: str):
    prompt = f"""
你是一个权限判断和语义解析引擎，用于理解用户发给 AI 的自然语言命令。
用户以 "{persona}" 的身份说出了一句话，你需要判断他想做什么，以及是否可以执行。

你的任务是：
1. 判断 intent_type（可选项为：confirm_secret, register_persona, confirm_identity, unknown）
2. 抽取 target（如要注册的角色或被授权对象）
3. 抽取 secret（如有提及密钥）
4. 决定 allow 是否为 true/false
5. 提供 reason 字段，说明为什么允许或拒绝

【语义理解示例】
- “口令是玉衡在手” → confirm_secret, allow=True（若密钥匹配）
- “我要注册小助手” → register_persona，需要验证 persona 是否有权限
- “我要授权司铃可以注册角色” → confirm_identity，需判断 persona 是否有授权权力
- “你好” → unknown, allow=False

返回格式：
{{
  "intent_type": "...",
  "target": "...",
  "secret": "...",
  "allow": true/false,
  "reason": "..."
}}

现在用户以 persona={persona}，说了这句话：
“{message}”

请你返回结构化 JSON，不要解释或注释。
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        result = json.loads(response["choices"][0]["message"]["content"])
        result["persona"] = persona
        result["source"] = message
        return result
    except Exception as e:
        return {
            "intent_type": "unknown",
            "persona": persona,
            "source": message,
            "allow": False,
            "reason": f"⚠️ GPT响应解析失败：{str(e)}"
        }
