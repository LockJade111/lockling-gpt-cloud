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

        # ✅ 解析意图
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = semantic_parser.parse_intent(message, persona)

        # ✅ 附加信息
        intent["source"] = message
        intent["persona"] = persona

        # ✅ 检查 intent_type
        intent_type = intent.get("intent_type", "")
        if not intent_type or intent_type == "unknown":
            return {
                "status": "fail",
                "reply": "❌ 无法识别指令意图。",
                "intent": intent,
                "persona": persona
            }

        # ✅ 权限要求判断（如果 intent 中要求权限）
        required = intent.get("requires")
        if required:
            allowed = check_permission.check_permission(persona, required)
            if not allowed:
                return {
                    "status": "fail",
                    "reply": "🚫 权限不足，拒绝操作。",
                    "intent": intent,
                    "persona": persona
                }

        # ✅ 调用分发器处理
        result = intent_dispatcher.dispatch_intent(intent)

        # ✅ 统一返回结构
        return {
            "status": "success" if "✅" in result.get("reply", "") else "fail",
            "reply": result.get("reply", "无应答"),
            "intent": result.get("intent", intent),
            "persona": persona
        }

    except Exception as e:
        return {
            "status": "error",
            "reply": f"💥 服务器内部错误：{str(e)}",
            "intent": {},
            "persona": "System"
        }
