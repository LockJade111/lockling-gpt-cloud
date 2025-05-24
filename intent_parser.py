import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(user_input: str, persona: str) -> dict:
    # 特例意图1：注册角色（优先识别，避免丢失）
    if "注册角色" in user_input or "创建角色" in user_input:
        name_match = re.search(r"(?:注册|创建)角色\s*(\S+)", user_input)
        permission_match = re.search(r"权限(?:为|是)?\s*(\S+)", user_input)
        tone_match = re.search(r"语气(?:为|是)?\s*(\S+)", user_input)

        return {
            "intent": "register_persona",
            "persona": persona,
            "new_name": name_match.group(1) if name_match else "未知",
            "permissions": [permission_match.group(1)] if permission_match else [],
            "tone": tone_match.group(1) if tone_match else "默认"
        }

    # 默认系统提示，适配主流意图解析
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_entry / query_logs / schedule_event / log_finance / log_customer / register_persona / unknown",
  "module": "logs / finance / schedule / customer / auth / unknown",
  "action": "write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "write / query / schedule / finance / unknown"
}}

请严格返回 JSON 格式，不要添加任何说明或多余语言。
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

        # 确保是标准 JSON
        if result.startswith("{") and result.endswith("}"):
            return json.loads(result)
        else:
            return {
                "intent": "unknown",
                "persona": persona,
                "error": "⚠️ GPT 返回非 JSON 格式"
            }

    except Exception as e:
        return {
            "intent": "unknown",
            "persona": persona,
            "error": str(e)
        }
