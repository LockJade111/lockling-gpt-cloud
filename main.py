from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai_helper import ask_gpt
from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
from notion_persona_writer import save_log_to_notion
from role_auto_register import register_from_intent
import re

app = FastAPI()

# ✅ 请求体模型
class ChatRequest(BaseModel):
    message: str
    persona: str = ""

# ✅ 角色识别逻辑：支持关键词 → 自动注册 → fallback
async def identify_persona_from_message(message: str) -> str:
    lowered = message.lower()
    if "司铃" in lowered or "秘书" in lowered:
        return "siling"
    if "军师猫" in lowered or "智谋执行官" in lowered:
        return "junshicat"
    if "军师" in lowered:
        return "junshi"
    if "锁灵" in lowered:
        return "lockling"
    if "徒弟" in lowered or "实习" in lowered:
        return "xiaotudi"

    # ✅ 自动注册逻辑：如“安排小艾协助”“请派小张去做”
    match = re.search(r"(安排|请派)([^，。\s]{1,6})(协助|帮忙|去做)", message)
    if match:
        name = match.group(2).strip()
        print(f"[自动注册] 捕捉到新角色意图：{name}")
        return await register_from_intent(name)

    return ""

# ✅ 意图识别：目前仅用 GPT 判断（可扩展）
async def identify_intent(message: str) -> str:
    if "安排" in message or "日程" in message:
        return "schedule"
    if "查询" in message or "是什么" in message or "能否" in message:
        return "query"
    if "记录" in message or "写入" in message or "日志" in message:
        return "log"
    return "other"

# ✅ 聊天主路由
@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message
    persona_id = await identify_persona_from_message(message) if not request.persona else request.persona

    if persona_id not in PERSONA_REGISTRY:
        return {"reply": f"未找到角色：{persona_id}", "persona": persona_id}

    persona = PERSONA_REGISTRY[persona_id]
    intent = await identify_intent(message)

    if not has_permission(persona_id, intent):
        return {
            "reply": f"{persona['name']}：对不起，您无权执行 {intent} 操作。",
            "persona": persona_id
        }

    prompt = persona["prompt"] + f"\n\n用户：{message}\n{persona['name']}："
    reply = await ask_gpt(prompt, persona_id)

    await save_log_to_notion(message, reply, persona_id, intent)
    return {"reply": reply, "persona": persona_id}
