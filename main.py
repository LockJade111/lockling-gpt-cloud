import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
from check_permission import get_persona_permissions
from intent_dispatcher import dispatch_intents

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ 跨域支持（开发/前端测试用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 权限判断（移除旧的 check_permission 引用）
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
            "reply": "❌ message 为空，无法处理。",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 自动意图识别（除非已传入完整 intent）
    if not intent or not isinstance(intent, dict) or not skip_parsing:
        intent = parse_intent(message, persona)

    intent_type = intent.get("intent_type", "unknown")
    required_permission = intent.get("requires_permission", "")

    print(f"🧠 intent_type={intent_type}, requires={required_permission}, persona={persona}")

    # ✅ 权限判断
    if not has_permission(persona, required_permission):
        reply = f"⛔ 权限不足（需要 {required_permission} 权限）"
        write_log_to_supabase(persona, message, intent, reply)
        return {
            "status": "denied",
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    # ✅ 分发执行
    result = dispatch_intents(intent, persona)
    reply = result.get("reply", "🤖 无响应")

    # ✅ 日志记录
    write_log_to_supabase(persona, message, intent, reply)

    return {
        "status": "success",
        "reply": reply,
        "intent": intent,
        "persona": persona
    }

@app.get("/")
async def root():
    return {"status": "✅ Lockling Cloud Ready"}
