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
async def chat(req: ChatRequest):
    msg = req.message.strip()
    persona = req.persona.strip()

    # ✅ 处理“修改密钥”请求
    if "密钥" in msg and any(kw in msg for kw in ["修改", "设置", "更换", "改为", "更新", "换成"]):
        print("[权限] 正在执行密钥更新判断")

        if not is_authorized_speaker(persona, msg):
            return {"reply": f"{persona}：您无权更改密钥。", "persona": "system"}

        if not contains_valid_passphrase(msg):
            return {"reply": "系统：未检测到有效口令，请说出授权密语。", "persona": "system"}

        new_key = extract_passphrase(msg)
        update_env_key_in_file(new_key)

        return {
            "reply": f"系统：口令已更新为「{new_key}」，下次部署即生效。",
            "persona": "system"
        }

    # ✅ 处理“赋予权限”请求
    if "赋予" in msg and "权限" in msg:
        print("[权限] 正在执行权限分配逻辑")

        data = await gpt_extract_permission_update(msg)
        target = data.get("name")
        requested_perm = data.get("permission")

        if not target or not requested_perm:
            return {"reply": "系统：解析失败，请明确角色与权限。", "persona": "system"}

        if not is_authorized_speaker(persona, msg):
            return {"reply": f"{persona}：您无权为 {target} 分配权限。", "persona": "system"}

        if target not in PERSONA_REGISTRY:
            return {"reply": f"系统：未找到角色 {target}。", "persona": "system"}

        if requested_perm in PERSONA_REGISTRY[target]["permissions"]:
            return {"reply": f"{target} 已拥有权限 {requested_perm}。", "persona": target}

        PERSONA_REGISTRY[target]["permissions"].append(requested_perm)
        return {"reply": f"{target}：权限已更新，获得 {requested_perm} 权限。", "persona": target}

    # ✅ 默认走 GPT 语义对话
    reply = await ask_gpt(msg, PERSONA_REGISTRY.get(persona, {}))
    return {"reply": reply, "persona": persona}
