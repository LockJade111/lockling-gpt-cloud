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

load_dotenv()

app = FastAPI()

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
    message = data.get("message")
    persona = data.get("persona", "Lockling 锁灵")

    if not message:
        return {
            "reply": "[系统错误] message 为空",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # 1. 意图识别
    intent_result = parse_intent(message, persona)

    # 防止返回 None
    if not intent_result or not isinstance(intent_result, dict):
        return {
            "reply": "❌ 意图识别失败：dispatch_intents() 无法识别结构",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # 2. 权限检查
    permission_required = intent_result.get("requires_permission", "")
    if not check_permission(persona, permission_required):
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result,
            "persona": persona
        }

    # 3. 调用模块执行
    try:
        reply_text = dispatch_intents(intent_result, persona)
    except Exception as e:
        return {
            "reply": f"❌ 调度失败: {str(e)}",
            "intent": intent_result,
            "persona": persona
        }

    # 4. 写入日志
    try:
        await write_log_to_supabase(message, reply_text, persona)
    except Exception as e:
        print("⚠️ Supabase 日志写入失败:", e)

    return {
        "reply": reply_text,
        "intent": intent_result,
        "persona": persona
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
