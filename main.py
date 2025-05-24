import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission, has_log_access
from supabase_logger import write_log_to_supabase, query_logs
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

# ✅ 主指令入口：/chat
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        # ✅ 语义解析：GPT解析意图或跳过
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = parse_intent(message, persona)

        intent["persona"] = persona
        intent["source"] = message

        # ✅ 权限核验
        if not check_secret_permission(persona, intent.get("secret", "")):
            intent["allow"] = False
            intent["reason"] = "密钥错误或未授权"
            reply = {
                "status": "fail",
                "reply": "❌ 身份验证失败，指令未执行。",
                "intent": intent,
                "persona": persona
            }
            write_log_to_supabase(intent, reply)
            return JSONResponse(reply)

        # ✅ 权限允许 → 派发执行
        intent["allow"] = True
        intent["reason"] = "身份验证成功"
        result = intent_dispatcher.dispatch_intents(intent)

        reply = {
            "status": "success",
            "reply": result,
            "intent": intent,
            "persona": persona
        }

        write_log_to_supabase(intent, reply)
        return JSONResponse(reply)

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"💥 服务异常：{str(e)}"
        })

# ✅ 日志查询接口：/log/query（将军专属）
@app.post("/log/query")
async def query_log(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    message = data.get("message", "").strip()

    # ✅ 权限控制：仅将军可查
    if not has_log_access(persona):
        return JSONResponse({
            "status": "fail",
            "reply": "🚫 当前身份无权查询日志。",
            "logs": []
        })

    # 简易关键词判断（可升级 GPT 理解）
    if "全部" in message or "最近" in message:
        logs = query_logs(limit=5)
    elif "助手" in message:
        logs = query_logs(persona="小助手")
    elif "司铃" in message:
        logs = query_logs(persona="司铃")
    else:
        logs = query_logs(persona=persona)

    return JSONResponse({
        "status": "success",
        "reply": f"✅ 为您找到 {len(logs)} 条日志记录：",
        "logs": logs
    })
