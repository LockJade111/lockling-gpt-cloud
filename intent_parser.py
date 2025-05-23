import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_entry / query_logs / schedule_event / finance_check / unknown",
  "module": "logs / roles / schedule / finance / unknown",
  "action": "read / write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "read / write / query / schedule / finance / unknown"
}}

严格返回 JSON 格式，不要添加解释或多余语言。
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
        result = response.choices[0].message["content"]
        # 安全转换返回值
        if result.strip().startswith("{") and result.strip().endswith("}"):
            return eval(result)
        else:
            return {"intent": "unknown"}
    except Exception as e:
        print("❌ GPT意图解析失败:", e)
        return {"intent": "unknown"}
