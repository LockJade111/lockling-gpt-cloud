import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from intent_parser import parse_intent
from intent_dispatcher import dispatch_intents

load_dotenv()

app = FastAPI()

# 启用 CORS 跨域支持
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
        return {"reply": "⚠️ message 不能为空", "persona": persona}

    try:
        # ✅ 调用 parse_intent 获取意图
        intent_result = parse_intent(message, persona)

        # ✅ 分发意图执行操作（如写入日志/排程等）
        reply = await dispatch_intents(intent_result, message)

        return {
            "reply": reply,
            "intent": intent_result,
            "persona": persona
        }

    except Exception as e:
        return {
            "reply": f"❌ 意图识别失败：{str(e)}",
            "intent": {"intent": "unknown"},
            "persona": persona
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
