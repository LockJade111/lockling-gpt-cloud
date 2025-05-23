import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_finance / schedule_event / log_customer / unknown",
  "module": "finance / schedule / customers / unknown",
  "action": "write / query / unknown",
  "persona": "{persona}",
  "requires_permission": "finance / schedule / customer / unknown"
}}

请严格输出 JSON，不要有多余文字。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
        )

        result = response.choices[0].message["content"].strip()

        if result.startswith("{") and result.endswith("}"):
            return json.loads(result)
        else:
            print("⚠️ 非法JSON结构:", result)
            return {"intent": "unknown"}
    except Exception as e:
        print("❌ GPT意图识别失败:", e)
        return {"intent": "unknown"}
