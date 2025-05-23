import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai_helper import ask_gpt
from supabase_logger import write_log_to_supabase
from dotenv import load_dotenv

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

    try:
        reply_text = ask_gpt(msg, persona)
    except Exception as e:
        return {"reply": f"[GPT ERROR] {str(e)}", "persona": persona}

    try:
        write_log_to_supabase(msg, reply_text, persona)
    except Exception as e:
        print("⚠️ Supabase 日志写入失败:", e)

    return {"reply": reply_text, "persona": persona}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
