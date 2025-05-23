import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
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
        return {"reply": "[系统错误] message 不能为空", "persona": persona}

    # 1. 意图识别
    try:
        intent_result = parse_intent(message, persona)
    except Exception as e:
        return {
            "reply": f"❌ 意图识别失败: {str(e)}",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # 2. 意图调度处理
    try:
        dispatch_result = dispatch_intents(intent_result, persona)
    except Exception as e:
        return {
            "reply": f"❌ 调度失败: {str(e)}",
            "intent": intent_result,
            "persona": persona
        }

    # 3. GPT 生成回复
    try:
        reply_text = ask_gpt(message, persona)
    except Exception as e:
        reply_text = f"[GPT ERROR] {str(e)}"

    # 4. 写入 Supabase 日志
    try:
        await write_log_to_supabase(message, reply_text, persona)
    except Exception as e:
        print("⚠️ 日志写入失败:", e)

    return {
        "reply": reply_text,
        "intent": intent_result,
        "persona": persona
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
