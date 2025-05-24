import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
import semantic_parser
import check_permission
# from supabase_logger import write_log_to_supabase  # 如果未启用可保持注释

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

        # ✅ 步骤1：语义解析
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = semantic_parser.parse_intent(message, persona)

        # ✅ 附加字段：source 与 persona
        intent["source"] = message
        intent["persona"] = persona

        # ✅ 步骤2：分发意图
        intent_type = intent.get("intent_type", "")
        if not intent_type:
            return {
                "status": "fail",
                "reply": "❌ dispatch_intents 无法识别 intent 类型: unknown",
                "intent": intent,
                "persona": persona
            }

        # ✅ 步骤3：处理意图逻辑
        reply = intent_dispatcher.dispatch_intent(intent)

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
