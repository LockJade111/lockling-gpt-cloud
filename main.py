import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from intent_dispatcher import dispatch_intents
from check_permission import get_persona_permissions

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 权限判断（保留兼容性）
def has_permission(persona, required):
    if not required:
        return True
    permissions = get_persona_permissions(persona)
    return required in permissions

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    message = data.get("message", "").strip()
    persona = data.get("persona", "Lockling 锁灵").strip()
    intent = data.get("intent")
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {
            "status": "fail",
            "reply": "❌ message 为空，无法处理。"
        }

    # ✅ fallback: 自动构建密钥意图
    if not intent or intent.get("intent_type") in ["", "unknown"]:
        if "玉衡在手" in message:
            intent = {
                "intent": "confirm_secret",
                "intent_type": "confirm_secret",
                "secret": "玉衡在手",
                "source": message
            }

    # ✅ 意图分发
    intent_result = dispatch_intents(intent, persona)

    # ✅ 权限判断
    required = intent_result.get("requires")
    has_access = has_permission(persona, required)

    if not has_access:
        return {
            "status": "success",
            "reply": "⛔️ 权限不足，拒绝操作。",
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 返回结果
    return {
        "status": "success",
        "reply": intent_result.get("reply", "✅ 指令已处理。"),
        "intent": intent_result,
        "persona": persona
    }
