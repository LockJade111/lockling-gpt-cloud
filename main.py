import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from intent_dispatcher import dispatch_intents
from check_permission import get_persona_permissions

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ 跨域支持（前端调试）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 权限判断（旧版本函数保留）
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

    # ✅ fallback intent 自动构建
    if not intent:
        intent = {
            "intent": "unknown",
            "intent_type": "unknown",
            "source": message
        }

    intent_type = intent.get("intent_type", "unknown")

    print(f"🧠 接收到意图类型: {intent_type}")

    # ✅ 分发处理逻辑
    result = dispatch_intents(intent, persona)

    return {
        "status": "success",
        "reply": result.get("reply", "⚠️ 无返回内容"),
        "intent": result.get("intent", intent),
        "persona": persona
    }
