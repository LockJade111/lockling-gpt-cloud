import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_intent(user_input: str, persona: str) -> dict:
    system_prompt = f"""
你是 LockJade 云脑的“意图判断器”，请从用户自然语言中提取以下五个字段：

```json
{{
  "intent": "...",
  "module": "...",
  "action": "...",
  "persona": "{persona}",
  "requires_permission": "..."
}}

常见意图示例：
- “张先生电话1234567890，换了锁150元” → log_customer
- “查王小姐服务记录” → query_customer
- “今天收了240元” → log_finance
- “安排李先生售后” → schedule_service
- “查询日志” → query_logs

返回标准 JSON，不解释。
"""
