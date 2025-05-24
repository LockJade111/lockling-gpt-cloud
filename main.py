import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase  # ✅ 日志模块

load_dotenv()

app = FastAPI()

# ✅ 启用 CORS（便于前端调试）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        # ✅ 意图解析（使用 GPT）
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = parse_intent(message, persona)

        intent["source"] = message
        intent["persona"] = persona

        # ✅ 意图类型为 unknown，直接返回
        if intent.get("intent_type") == "unknown":
            return {
                "status": "success",
                "reply": {
                    "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent.get('intent_type')}",
                    "intent": intent
                },
                "intent": intent,
                "persona": persona
            }

        # ✅ 调度意图执行
        reply = intent_dispatcher.dispatch_intents(intent)

        # ✅ 写入日志（无论成功失败）
        write_log_to_supabase(
            message=message,
            persona=persona,
            intent_result=reply.get("intent", {}),
            reply=reply.get("reply", "")
        )

        return {
            "status": "success",
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    except Exception as e:
        return {
            "status": "error",
            "reply": f"💥 系统异常：{str(e)}"
        }
