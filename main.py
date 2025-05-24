import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
import semantic_parser  # ✅ 确保此模块存在并导入 parse_intent
import check_permission
# from supabase_logger import write_log_to_supabase  # 如你尚未启用日志模块，可先注释

load_dotenv()

app = FastAPI()

# ✅ CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 主接口
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        # ✅ 意图识别
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = semantic_parser.parse_intent(message)
            intent["source"] = message
            intent["persona"] = persona

        intent_type = intent.get("intent_type", "")
        if not intent_type:
            return {
                "status": "fail",
                "reply": "❌ 无法识别意图。",
                "intent": intent,
                "persona": persona
            }

        # ✅ 分发处理
        result = intent_dispatcher.dispatch_intent(intent)
        return {
            "status": "success" if "✅" in result["reply"] else "fail",
            "reply": result["reply"],
            "intent": result.get("intent", intent),
            "persona": persona
        }

    except Exception as e:
        print(f"🔥 错误：{e}")
        return {
            "status": "error",
            "reply": f"💥 服务器内部错误：{str(e)}",
            "intent": {},
            "persona": "System"
        }
