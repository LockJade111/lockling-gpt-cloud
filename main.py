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

# ✅ 启用跨域请求支持
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

    if not message:
        return {
            "reply": "❌ message 为空，无法处理",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 分析意图
    intent_result = parse_intent(message, persona)
    print(f"🌐 调试中：intent_result = {intent_result}")

    # ✅ 权限检查
    required = intent_result.get("requires_permission", "")
    intent_type = intent_result.get("intent_type", "")
    is_allowed = check_permission(persona, required, intent_type, intent_result)
    print(f"🔒 权限校验：{is_allowed}")

    if not is_allowed:
        reply = "⛔ 权限不足，拒绝操作"
        write_log_to_supabase(persona, message, intent_result, reply)
        return {
            "reply": reply,
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 执行意图处理
    result = dispatch_intents(intent_result, persona)
    reply = result.get("reply", "🤖 未知响应")
    print(f"📤 最终回复：{reply}")

    # ✅ 日志写入（含回复）
    write_log_to_supabase(persona, message, intent_result, reply)

    return {
        "reply": reply,
        "intent": intent_result,
        "persona": persona
    }
