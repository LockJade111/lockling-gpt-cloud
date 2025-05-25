import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # ✅ 确保加载 .env 文件中的 OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str):
    persona_intro = f"你现在以 {persona} 的身份处理指令。身份等级将影响你是否有权限执行某些操作。\n\n"

    prompt = persona_intro + """
你是一个权限与语义解析系统，负责将用户发出的自然语言命令，转换为结构化意图。

系统中有多种身份（persona），例如：
🟢 persona="将军"：系统最高权限者，可注册、授权、撤销、删除等敏感操作，需提供密钥（如“玉衡在手”）。
🟡 persona="司铃"、"小助手" 等：默认无注册/授权权限，需被“将军”授权后才可操作。

你需识别以下意图类型（intent_type）：

1. confirm_secret       → 身份验证，如 “口令是玉衡在手”
2. register_persona     → 注册角色，如 “我要注册角色 小助手”
3. confirm_identity     → 授权他人，如 “我要授权 司铃 注册权限”
4. revoke_identity      → 取消授权，如 “我要取消 司铃 的注册权限”
5. delete_persona       → 删除角色，如 “我要删除角色 小助手”
6. authorize            → 授权他人权限（简略指令，如 “授权小艾只读”）
7. request_secret       → 要求输入密钥（如“我是将军”）
8. unknown              → 无法识别或不属于以上类型的内容

【输入】用户自然语言  
【输出】格式必须为 JSON，无注释，字段包括：

{
  "intent_type": "intent 类型（如 confirm_secret）",
  "target": "目标对象，如某个角色名",
  "permissions": ["权限列表，若无则为空数组"],
  "secret": "口令/密钥，若无则为空字符串",
  "allow": true 或 false,
  "reason": "若拒绝或失败，请写明原因"
}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt.strip()},
            {"role": "user", "content": message}
        ]
    )

    try:
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "status": "error",
            "reply": f"🐛 无法理解指令结构: {str(e)}",
            "intent": {}
        }
