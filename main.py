import os
import uvicorn
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

# ✅ CORS 设置
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
    message = data.get("message", "")
    persona = data.get("persona", "Lockling 锁灵")

    if not message:
        return {
            "reply": "❌ message 为空，无法处理",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # ✅ 意图识别
    intent_result = parse_intent(message, persona)
    print(f"🌐 调试中：intent_result = {intent_result}")

    intent_type = intent_result.get("intent_type", "unknown")

    # ✅ 权限检查
    has_permission = check_permission(
        persona=persona,
        required=intent_result.get("requires_permission", ""),
        intent_type=intent_type,
        intent=intent_result
    )
    print(f"🔐 权限校验：{has_permission}")

    if not has_permission:
        return {
            "reply": "⛔ 权限不足，拒绝操作",
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 分发处理意图
    result = dispatch_intents(intent_result, persona)
    print(f"📦 分发结果：{result}")

    # ✅ 写入日志
    write_log_to_supabase(message, persona, intent_result, result["reply"])

    return {
        "reply": result["reply"],
        "intent": result.get("intent", intent_result),
        "persona": persona
    }

# ✅ 启动入口（如需本地调试）
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
