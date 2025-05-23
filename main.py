import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from gpt_intent_parser import gpt_parse_intents
from intent_dispatcher import dispatch_intents

load_dotenv()

app = FastAPI()

# 允许跨域（前端调试等）
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
        return {"reply": "⚠️ message 不能为空", "persona": persona}

    # 1. GPT结构化意图解析
    try:
        intent_list = gpt_parse_intents(msg, persona)
    except Exception as e:
        return {"reply": f"❌ GPT 意图识别失败：{str(e)}", "persona": persona}

    # 2. 意图派发（权限校验 + 行为执行）
    dispatch_result = dispatch_intents(intent_list)

    return {
        "reply": "✅ 指令已识别并派发完毕",
        "persona": persona,
        "dispatch_result": dispatch_result
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
