import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
from check_permission import check_permission
from intent_dispatcher import dispatch_intents

# ✅ 加载 .env 文件
load_dotenv()

app = FastAPI()

# ✅ 启用 CORS，允许任意跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    message = data.get("message", "").strip()
    persona = data.get("persona", "Lockling 锁灵").strip()
    intent = data.get("intent")  # 可选外部注入意图（如 curl 测试）
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {
            "reply": "❌ message 为空，无法处理。",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 若未提供 intent 或明确要求重新解析，则使用 GPT 自动解析
    if not intent or not isinstance(intent, dict) or not skip_parsing:
        intent = parse_intent(message, persona)

    # ✅ 权限判断
    intent_type = intent.get("intent_type", "unknown")
    required = intent.get("requires_permission", "")
    is_allowed = check_permission(persona, required, intent_type, intent)

    if not is_allowed:
        reply = "⛔ 权限不足，拒绝操作"
        write_log_to_supabase(persona, message, intent, reply)
        return {
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    # ✅ 分发意图执行逻辑
    result = dispatch_intents(intent, persona)
    reply = result.get("reply", "🤖 未知响应")

    # ✅ 写入日志
    write_log_to_supabase(persona, message, intent, reply)

    return {
        "reply": reply,
        "intent": intent,
        "persona": persona
    }

@app.get("/")
async def root():
    return {"status": "✅ Lockling GPT Cloud API 正常运行"}
