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

    # ✅ 日志写入（supabase 可选）
    write_log_to_supabase(persona, message, intent_result)

    # ✅ 分发意图 + 权限判断
    result = dispatch_intents(intent_result, persona)

    # ✅ 返回包含意图与身份的完整结构
    result["intent"] = intent_result
    result["persona"] = persona
    return result

@app.get("/")
async def root():
    return {"status": "✅ Lockling AI 核心系统已启动"}
