import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
from check_permission import check_permission
from intent_dispatcher import dispatch_intents

# ✅ 加载环境变量（.env）
load_dotenv()

app = FastAPI()

# ✅ CORS 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许全部来源，前端调试用
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    message = data.get("message", "").strip()
    persona = data.get("persona", "Lockling 锁灵").strip()
    intent = data.get("intent")  # 可传入完整 intent 结构（跳过 GPT）
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {
            "reply": "❌ message 为空，无法处理。",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 使用 GPT 自动解析 intent（除非传入 intent 且要求跳过解析）
    if not intent or not isinstance(intent, dict) or skip_parsing is False:
        intent = parse_intent(message, persona)

    intent_type = intent.get("intent_type", "unknown")
    required = intent.get("requires_permission", "")

    # ✅ 权限判断
    is_allowed = check_permission(persona, required, intent_type, intent)
    if not is_allowed:
        reply = "⛔ 权限不足，拒绝操作"
        write_log_to_supabase(persona, message, intent, reply)
        return {
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    # ✅ 调用 dispatcher 分发执行
    result = dispatch_intents(intent, persona)
    reply = result.get("reply", "🤖 未知响应")

    # ✅ 写入 Supabase 日志
    write_log_to_supabase(persona, message, intent, reply)

    return {
        "reply": reply,
        "intent": intent,
        "persona": persona
    }

@app.get("/")
async def root():
    return {"status": "✅ Lockling GPT Cloud API 正常运行"}
