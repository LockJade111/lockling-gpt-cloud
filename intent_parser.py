import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(user_input: str, persona: str) -> dict:
    # ✅ 口头授权识别：「密钥玉衡在手，授权军师猫可以注册新角色」
    if "密钥" in user_input and "授权" in user_input and "注册" in user_input:
        grantee_match = re.search(r"授权\s*(\S+?)\s*(可以)?注册", user_input)
        if grantee_match:
            grantee = grantee_match.group(1)
            return {
                "intent": "grant_permission",
                "persona": persona,
                "grantee": grantee,
                "permission": "register_persona",
                "source": user_input  # ✅ 添加原始语句来源
            }

    # ✅ 注册角色识别：「注册角色小艾，权限为 query，语气为活泼」
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
            "source": user_input  # ✅ 添加原始语句来源
        }

    # ✅ 其他意图默认由 GPT 辅助判断
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
        if result.startswith("{") and result.endswith("}"):
            parsed = json.loads(result)
            parsed["source"] = user_input  # ✅ 强制添加 source 字段
            return parsed
        else:
            return {
                "intent": "unknown",
                "persona": persona,
                "error": "GPT 返回格式非法",
                "source": user_input
            }

    except Exception as e:
        return {
            "intent": "unknown",
            "persona": persona,
            "error": str(e),
            "source": user_input
        }
