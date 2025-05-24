import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(user_input: str, persona: str) -> dict:
    # ✅ 一句话式口令授权：「我是将军，我要授权军师猫注册新角色，密钥是玉衡在手」
    if any(kw in user_input for kw in ["授权", "注册", "密钥", "口令"]):
        persona_match = re.search(r"我是(\S+)", user_input)
        grantee_match = re.search(r"授权(\S+?)注册", user_input)
        permission_match = "register_persona" if "注册新角色" in user_input else None
        secret_match = re.search(r"(?:密钥|口令)[为是:]?\s*([^\s，。；：]*)", user_input)

        if persona_match and grantee_match and permission_match and secret_match:
            return {
                "intent": "grant_permission",
                "persona": persona_match.group(1),
                "grantee": grantee_match.group(1),
                "permission": permission_match,
                "secret": secret_match.group(1),
                "source": user_input
            }

    # ✅ 注册角色意图
    if "注册角色" in user_input or "创建角色" in user_input:
        name_match = re.search(r"(?:注册|创建)角色\s*([\u4e00-\u9fa5A-Za-z0-9_]+)", user_input)
        permission_match = re.search(r"权限(?:为|是)?\s*([a-zA-Z_]+)", user_input)
        tone_match = re.search(r"语气(?:为|是)?\s*([\u4e00-\u9fa5A-Za-z]+)", user_input)

        return {
            "intent": "register_persona",
            "persona": persona,
            "new_name": name_match.group(1) if name_match else "未知",
            "permissions": [permission_match.group(1)] if permission_match else [],
            "tone": tone_match.group(1) if tone_match else "默认",
            "source": user_input
        }

    # ✅ 默认调用 GPT 模型解析
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，你的任务是从用户自然语言中提取结构化意图，并用以下 JSON 格式回答：

{{
  "intent": "log_entry / query_logs / schedule_event / log_finance / log_customer / register_persona / grant_permission / unknown",
  "module": "logs / finance / schedule / customer / auth / unknown",
  "action": "write / query / schedule / unknown",
  "persona": "{persona}",
  "requires_permission": "write / query / schedule / finance / register_persona / unknown"
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
        parsed = json.loads(result)
        parsed["source"] = user_input  # 强制加入原文
        return parsed
    except Exception as e:
        return {
            "intent": "unknown",
            "persona": persona,
            "error": str(e),
            "source": user_input
        }
