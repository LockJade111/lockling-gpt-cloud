import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_entry / query_logs / log_finance / schedule_event / unknown",
  "module": "logs / finance / schedule / roles / unknown",
  "action": "read / write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "read / write / query / schedule / finance / unknown"
}}

⚠️ 严格返回 JSON 格式，禁止添加多余说明、代码块语法或前后缀。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
        )
        content = response.choices[0].message["content"].strip()

        # 尝试强制去掉代码块语法
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(content)

        required_keys = ["intent", "module", "action", "persona", "requires_permission"]
        if all(k in parsed for k in required_keys):
            return parsed
        else:
            print("⚠️ GPT返回结构缺失:", parsed)
            return None

    except Exception as e:
        print("❌ GPT意图解析失败:", e)
        return None
