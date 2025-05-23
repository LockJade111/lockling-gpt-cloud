import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from finance_helper import log_finance

from intent_parser import parse_intent
intent_result = parse_intent(message, persona)
from intent_dispatcher import dispatch_intents

load_dotenv()

app = FastAPI()

# 启用 CORS，支持跨域调用
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

    # 意图解析
    try:
        intent_result = parse_intents(msg, persona)
    except Exception as e:
        return {
            "reply": f"❌ 意图识别失败：{str(e)}",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

    # 根据意图派发模块处理
    try:
        result = await dispatch_intents(intent_result, msg, persona)
        return result
    except Exception as e:
        return {
            "reply": f"❌ 模块处理失败：{str(e)}",
            "intent": intent_result,
            "persona": persona
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
