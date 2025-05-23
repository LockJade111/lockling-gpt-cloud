import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，请从用户自然语言中提取以下结构（用JSON返回）：

{{
  "intent": "log_entry / query_logs / log_finance / schedule_service / unknown",
  "module": "logs / finance / schedule / roles / unknown",
  "action": "read / write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "read / write / query / schedule / finance / unknown"
}}

只返回 JSON，不要加代码块符号、解释或注释。
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
        content = response.choices[0].message["content"].strip()

        # 清理 GPT 多余标记
        if content.startswith("```json"):
            content = content.replace("```json", "").strip()
        if content.endswith("```"):
            content = content.replace("```", "").strip()

        # 安全解析 JSON
        try:
            result = json.loads(content)
            if isinstance(result, dict) and "intent" in result:
                return result
            else:
                return {"intent": "unknown"}
        except Exception as e:
            print("⚠️ JSON解析失败：", e)
            return {"intent": "unknown"}

    except Exception as e:
        print("❌ GPT调用失败：", e)
        return {"intent": "unknown"}
