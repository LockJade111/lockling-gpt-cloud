from notion_logger import write_log_to_notion
from fastapi import FastAPI
from pydantic import BaseModel
from auth_core import is_authorized_speaker, contains_valid_passphrase, extract_passphrase
from openai_helper import ask_gpt, gpt_extract_key_update
from env_writer import update_env_key_in_file
from persona_registry import PERSONA_REGISTRY

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    persona: str

@app.post("/chat")
async def chat(payload: dict):
    message = payload.get("message", "")
    persona = payload.get("persona", "")

    # 权限分配指令识别
    if "授权" in message and ("为" in message or "赋予" in message):
        target, requested_perm = gpt_extract_permission_update(message)
        if not target or not requested_perm:
            return {"reply": "系统：解析失败，请明确角色与权限。", "persona": "system"}

        if not is_authorized_speaker(persona, message):
            return {"reply": f"{persona}：您无权为 {target} 分配权限。", "persona": "system"}

        if target not in PERSONA_REGISTRY:
            return {"reply": f"系统：未找到角色 {target}。", "persona": "system"}

        if requested_perm in PERSONA_REGISTRY[target]["permissions"]:
            return {"reply": f"{target} 已拥有权限 {requested_perm}。", "persona": target}

        PERSONA_REGISTRY[target]["permissions"].append(requested_perm)
        return {"reply": f"{target}：权限已更新，获得 {requested_perm} 权限。", "persona": target}

    # ✅ 默认走 GPT 语义对话
    reply_text = await ask_gpt(message, PERSONA_REGISTRY.get(persona, {}))
    response = {"reply": reply_text, "persona": persona}

    # 写入 Notion 日志
    try:
        write_log_to_notion(message, reply_text, persona)
    except Exception as e:
        print("⚠️️ Notion 日志写入失败:", e)

    return response
