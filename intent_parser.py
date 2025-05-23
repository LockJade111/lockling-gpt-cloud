import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，请从用户自然语言中提取以下五个字段：

```json
{{
  "intent": "...",                // 如：log_entry、query_logs、log_finance、schedule_service
  "module": "...",                // 如：logs、finance、schedule、roles
  "action": "...",                // 如：read、write、query、schedule
  "persona": "{persona}",         // 系统会自动注入
  "requires_permission": "..."    // 与 action 对应，如 write/query/finance
}}
"""
