import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
import semantic_parser
import check_permission
# from supabase_logger import write_log_to_supabase  # 如尚未启用，可注释

load_dotenv()

app = FastAPI()

# ✅ 跨域设置
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

        # ✅ 语义解析与意图识别
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = semantic_parser.parse_intent(message, persona)
            intent["source"] = message
            intent["persona"] = persona

        intent_type = intent.get("intent_type", "")
        if not intent_type:
            return {
                "status": "fail",
                "reply": "❌ 无法识别意图类型。",
                "intent": intent,
                "persona": persona
            }

        # ✅ 权限检查
        required = intent.get("requires", "")
        if required:
            has_permission = check_permission.check_permission(persona, required)
            if not has_permission:
                return {
                    "status": "fail",
                    "reply": "🚫 权限不足，拒绝操作。",
                    "intent": intent,
                    "persona": persona
                }

        # ✅ 调用 intent 分发器处理
        reply = await intent_dispatcher.dispatch_intent(intent)

        # ✅ 可选日志记录
        # write_log_to_supabase(persona, message, intent, reply)

        return {
            "status": "success",
            "reply": reply,
            "intent": intent,
            "persona": persona
        }

    except Exception as e:
        return {
            "status": "error",
            "reply": f"💥 服务器内部错误：{str(e)}",
            "intent": {},
            "persona": "System"
        }
