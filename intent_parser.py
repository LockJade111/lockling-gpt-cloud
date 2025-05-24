import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_entry / query_logs / schedule_event / log_finance / log_customer / unknown",
  "module": "logs / finance / schedule / customer / unknown",
  "action": "write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "write / query / schedule / finance / unknown"
}}

严格返回 JSON 格式，不要添加解释或多余语言。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()

        # 尝试解析成 dict
        if result.startswith("{") and result.endswith("}"):
            return json.loads(result)
        else:
            return {"intent": "unknown", "error": "⚠️ GPT 返回非标准结构"}

    except Exception as e:
        print("❌ GPT意图解析失败:", e)
        return {"intent": "unknown", "error": str(e)}
