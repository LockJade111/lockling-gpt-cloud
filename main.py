from fastapi import FastAPI, Request
from openai_helper import ask_gpt
from persona_registry import get_persona
from notion_helper import save_to_notion

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    persona_id = data.get("persona", "junshi")  # 默认是军师

    persona = get_persona(persona_id)
    reply = await ask_gpt(message, persona)

    # ✅ 正确插入在这里：
    await save_to_notion(persona["name"], message, reply)

    return {
        "reply": reply,
        "persona": persona["name"]
    }
