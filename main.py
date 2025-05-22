from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
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
    
    persona = PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["lockling"])

    # ✅ 正确缩进（保持与上一行一致的4空格）
    if not has_permission(persona_id, "schedule"):
        return {
            "reply": f"{persona['name']}：对不起，您无权执行调度模块。",
            "persona": persona["name"]
        }

    reply = await ask_gpt(message, persona)
    await save_to_notion(persona["name"], message, reply) 
    styled_reply = get_persona_response(persona_id, reply)
    
    return {
        "reply": styled_reply,
        "persona": persona["name"]
    }
