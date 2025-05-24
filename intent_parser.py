import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的意图判断器，职责是根据用户输入判断其意图，并以 JSON 格式返回结果。
请仅返回以下格式的 JSON，不允许自然语言或解释。

示例格式：
{{
  "intent": "log_finance",
  "module": "finance",
  "action": "write",
  "persona": "{persona}",
  "requires_permission": "finance"
}}

如无法识别意图，请返回：
{{
  "intent": "unknown",
  "persona": "{persona}"
}}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_input.strip()}
            ],
            temperature=0.1,
        )
        content = response.choices[0].message["content"].strip()

        # 清洗 GPT 输出
        if content.startswith("```json"):
            content = content.replace("```json", "").strip()
        if content.endswith("```"):
            content = content.replace("```", "").strip()

        # 尝试解析为 JSON
        parsed = json.loads(content)
        return parsed

    except Exception as e:
        return {
            "intent": "unknown",
            "persona": persona,
            "error": str(e)
        }
