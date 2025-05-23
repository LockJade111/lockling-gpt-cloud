import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from intent_parser import parse_intents
from intent_dispatcher import dispatch_intents

load_dotenv()

app = FastAPI()

# 启用 CORS，方便前端或外部调用
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
    persona = data.get("persona", "Lockling 锁灵")  # 默认角色

    if not msg:
        return {"reply": "⚠️ message 不能为空", "persona": persona}

    # 1. 使用意图解析模块分析消息
    try:
        intent_list = parse_intents(msg, persona)
    except Exception as e:
        return {
            "reply": f"❌ 意图识别失败：{str(e)}",
            "persona": persona
        }

    # 2. 根据意图执行任务（权限检查 + 模块调度）
    try:
        dispatch_result = dispatch_intents(intent_list)
    except Exception as e:
        return {
            "reply": f"❌ 指令执行失败：{str(e)}",
            "persona": persona
        }

    return {
        "reply": "✅ 指令已识别并派发完毕",
        "persona": persona,
        "dispatch_result": dispatch_result
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
