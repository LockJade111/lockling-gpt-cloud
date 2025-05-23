import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取意图，并用以下结构回答：

{{
  "intent": "log_entry / query_logs / schedule_event / finance_check / unknown",
  "module": "logs / roles / schedule / finance / unknown",
  "action": "read / write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "read / write / query / schedule / finance / unknown"
}}

只返回 JSON，不做解释，不带自然语言。
"""

    user_message = {"role": "user", "content": user_input}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                user_message
            ],
            temperature=0.2
        )

        parsed = response.choices[0].message['content']
        return eval(parsed) if parsed.startswith("{") else {"intent": "unknown"}

    except Exception as e:
        print("❌ GPT解析失败:", e)
        return {"intent": "unknown"}
