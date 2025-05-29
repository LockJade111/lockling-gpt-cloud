# generate_reply_with_gpt.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_reply(intent: dict) -> str:
    persona = intent.get("persona", "Lockling")
    intent_type = intent.get("intent_type", "unknown")
    target = intent.get("target", "")
    permissions = intent.get("permissions", [])
    
    # 可以加入风格语气设定
    prompt = f"""
你是 {persona}，一位亲切智慧的门店守护精灵，性格亲和、专业，善于解释系统指令。
请用自然语言回复用户的请求，结合 intent_type 做出回答，不用重复结构化内容。

当前意图类型：{intent_type}
操作目标：{target}
权限内容：{permissions}

注意：
- 回复应口吻自然、友好、有温度；
- 不要返回 JSON 或代码结构；
- 如果是注册类的操作，可引导下一步；
- 如果无法判断意图，请礼貌说明“我不太明白”。

请你现在生成回复。
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "请生成回复"}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ 生成回复失败：{str(e)}"
