import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase
from supabase import create_client, Client

# ✅ 环境变量加载
load_dotenv()

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ FastAPI 初始化
app = FastAPI()

# ✅ 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ /chat：主指令入口
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

        # ✅ 未识别意图类型
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

        # ✅ 执行意图
        reply = intent_dispatcher.dispatch_intents(intent)

        # ✅ 写入操作日志
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

# ✅ /logs：操作日志查看接口（最近50条）
@app.get("/logs")
async def get_logs():
    try:
        result = supabase.table("logs").select("*").order("timestamp", desc=True).limit(50).execute()
        return {
            "status": "success",
            "count": len(result.data),
            "logs": result.data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"日志查询失败：{str(e)}"
        }
