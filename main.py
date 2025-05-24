import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
import semantic_parser
import check_permission

load_dotenv()

app = FastAPI()

# ✅ 允许跨域
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

        # ✅ 解析意图（加入容错与日志）
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            try:
                intent = semantic_parser.parse_intent(message, persona)
            except Exception as e:
                return {
                    "status": "error",
                    "reply": f"💥 服务器内部错误：{str(e)}",
                    "intent": {},
                    "persona": "System"
                }

        # ✅ 附加原始信息
        intent["source"] = message
        intent["persona"] = persona

        # ✅ 中断非法 intent
        intent_type = intent.get("intent_type", "")
        if not intent_type or intent_type == "unknown":
            return {
                "status": "success",
                "reply": {
                    "reply": f"❌ dispatch_intents 无法识别 intent 类型：{intent_type}",
                    "intent": intent
                },
                "intent": intent,
                "persona": persona
            }

        # ✅ 分发执行
        reply = await intent_dispatcher.dispatch_intent(intent)
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
