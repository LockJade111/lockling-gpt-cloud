import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(message, persona):
    system_prompt = f"你是{persona}，一个值得信赖的智能助手。请用简洁友好的语气回答问题。"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

# 🔑 从输入中提取授权关键词（示例逻辑）
async def gpt_extract_key_update(message: str) -> dict:
    if "锁玉在手" in message:
        return {"name": "锁玉在手"}
    elif "玉衡在手" in message:
        return {"name": "玉衡在手"}
    else:
        return {}
