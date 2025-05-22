import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_gpt(user_input: str, persona: dict) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": persona["prompt"]},
                {"role": "user", "content": user_input}
            ],
            temperature=0.85,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT ERROR] {str(e)}"
