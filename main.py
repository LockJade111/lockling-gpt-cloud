from fastapi import FastAPI, Request
from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
from openai_helper import ask_gpt
from notion_helper import save_to_notion

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    persona_id = data.get("persona", "junshi")  # 默认是军师

    persona = PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["lockling"])

    # ✅ 权限判断逻辑（以关键词“调度”为例）
    if "调度" in message and not has_permission(persona_id, "schedule"):
        return {
            "reply": f"{persona['name']}：对不起，您无权执行调度模块。",
            "persona": persona["name"]
        }

    # ✅ 正常对话流程
    reply = await ask_gpt(message, persona)
    await save_log_to_notion(persona["name"], message, reply)
    await save_to_notion(persona["name"], message, reply)
    styled_reply = get_persona_response(persona_id, reply)
    
    return {
        "reply": styled_reply,
        "persona": persona["name"]
    }
