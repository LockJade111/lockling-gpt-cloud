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

# ✅ 跨域设置（允许前端访问）
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

    # ✅ 1. 意图识别
    intent_result = parse_intent(message, persona)

    if not isinstance(intent_result, dict) or intent_result.get("intent") == "unknown":
        return {
            "reply": "❌ 意图识别失败：dispatch_intents() 无法识别结构",
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 2. 权限判断
    intent_type = intent_result.get("intent_type")
    required = intent_result.get("requires_permission", "")
    allowed = check_permission(persona, required, intent_type=intent_type, intent=intent_result)

    if not allowed:
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 3. 派发执行逻辑
    reply = dispatch_intents(intent_result, persona)

    # ✅ 4. 写入日志
    write_log_to_supabase(message, persona, intent_result, reply)

    return {
        "reply": reply,
        "intent": intent_result,
        "persona": persona
    }

# ✅ 启动本地测试（可忽略，Render 不使用此入口）
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
