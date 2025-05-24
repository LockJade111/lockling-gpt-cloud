import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
from check_permission import check_permission
from intent_dispatcher import dispatch_intents

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ CORS 设置：允许跨域访问
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
    intent = data.get("intent")  # 用户是否直接传了intent结构
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {
            "reply": "❌ message 为空，无法处理。",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 如果没有传入 intent，就用 GPT 解析意图
    if not intent or not isinstance(intent, dict) or skip_parsing is False:
        intent = parse_intent(message, persona)

    intent_type = intent.get("intent_type", "")
    required = intent.get("requires_permission", "")

    print(f"📥 收到请求：persona={persona}, intent_type={intent_type}, message={message}")

    # ✅ 权限校验
    is_allowed = check_permission(persona, required, intent_type, intent)
    if not is_allowed:
        reply = "⛔ 权限不足，拒绝操作"
        write_log_to_supabase(persona, message, intent, reply)
        return {
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    # ✅ 分发处理意图
    response = dispatch_intents(intent, persona)
    reply = response.get("reply", "🤖 未知响应")
    print(f"📤 回复：{reply}")

    # ✅ 写入日志
    write_log_to_supabase(persona, message, intent, reply)

    # ✅ 返回结构
    return {
        "reply": reply,
        "intent": intent,
        "persona": persona
    }

@app.get("/")
async def root():
    return {"status": "✅ Lockling GPT Cloud API 已启动"}
