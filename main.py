import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from intent_parser import parse_intent
from check_permission import check_permission

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
    msg = data.get("message")
    persona = data.get("persona", "Lockling 锁灵")

    if not msg:
        return {"reply": "[系统错误] message 为空", "persona": persona}

    # 1. 意图解析
    intent_result = parse_intent(msg, persona)

    # 2. 权限判断
    required_perm = intent_result.get("requires_permission", "")
    if not check_permission(persona, required_perm):
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result,
            "persona": persona
        }

    # 3. GPT 生成回复
    try:
        reply_text = ask_gpt(msg, persona)
    except Exception as e:
        return {"reply": f"[GPT 错误] {str(e)}", "persona": persona}

    # 4. 日志写入（仅在 intent 为 log_entry 或有 write 权限时）
    if intent_result["intent"] == "log_entry" or "write" in required_perm:
        try:
            await write_log_to_supabase(msg, reply_text, persona)
        except Exception as e:
            print("⚠️ Supabase 日志写入失败:", e)

    return {
        "reply": reply_text,
        "intent": intent_result,
        "persona": persona
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
