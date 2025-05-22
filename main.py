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
    persona_id = data.get("persona", "junshi")

    persona = PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["lockling"])

    # 🧠 意图识别：让GPT判断行为类型
    intent_prompt = (
        f"请判断这句话属于哪种行为类型：调度、查询、控制、问候、播报、其他。\n"
        f"只返回一个英文关键词（schedule, query, control, greeting, report, other），不要解释。\n"
        f"\n输入：{message}\n输出："
    )
    intent = await ask_gpt(intent_prompt, persona)
    intent = intent.lower().strip()

    # ✅ 权限判断
    if not has_permission(persona_id, intent):
        return {
            "reply": f"{persona['name']}：对不起，您无权执行 {intent} 操作。",
            "persona": persona["name"]
        }

    # ✅ 正常对话流程
    reply = await ask_gpt(message, persona)

    # ✅ 日志记录（含意图）
    await save_log_to_notion(persona["name"], message, reply, intent)
    await save_to_notion(persona["name"], message, reply)

    styled_reply = get_persona_response(persona_id, reply)

    return {
        "reply": styled_reply,
        "persona": persona["name"]
    }
