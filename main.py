import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent  # ✅ 使用新版 GPT 解析器
from check_permission import check_secret_permission  # ✅ 本地密钥判断

load_dotenv()

app = FastAPI()

# ✅ 启用跨域支持（前端调试友好）
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

        # ✅ GPT 解析意图
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = parse_intent(message, persona)

        intent["source"] = message
        intent["persona"] = persona

        # ✅ 阻止 unknown 意图进入执行流
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

        # ✅ 若需要密钥校验（如 confirm_secret / confirm_identity）
        if intent.get("intent_type") in ["confirm_secret", "confirm_identity"]:
            secret = intent.get("secret", "").strip()
            if not check_secret_permission(persona, secret):
                return {
                    "status": "fail",
                    "reply": "🚫 密钥错误，身份验证失败。",
                    "intent": intent,
                    "persona": persona
                }

        # ✅ GPT 判断不允许执行
        if intent.get("allow") is False:
            return {
                "status": "fail",
                "reply": f"⚠️ GPT 拒绝执行操作：{intent.get('reason', '权限不足')}",
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
