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

# ✅ 主接口 /chat：指令识别 → 权限验证 → 分发 → 日志写入
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        # ✅ 语义解析
        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = parse_intent(message, persona)

        intent["persona"] = persona
        intent["source"] = message

        # ✅ 权限校验
        if not check_secret_permission(persona, intent.get("secret", "")):
            intent["allow"] = False
            intent["reason"] = "密钥错误或未授权"
            reply = {
                "status": "fail",
                "reply": "❌ 身份验证失败，指令未执行。",
                "intent": intent,
                "persona": persona
            }
            write_log_to_supabase(message, persona, intent, reply["reply"])
            return JSONResponse(reply)

        # ✅ 允许执行 → 分发意图
        intent["allow"] = True
        intent["reason"] = "身份验证成功"
        result = intent_dispatcher.dispatch_intents(intent)

        reply = {
            "status": "success",
            "reply": result,
            "intent": intent,
            "persona": persona
        }

        write_log_to_supabase(message, persona, intent, result)
        return JSONResponse(reply)

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"💥 服务异常：{str(e)}"
        })

# ✅ 日志查询接口 /log/query：支持分页与多条件筛选
@app.post("/log/query")
async def query_log(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    limit = int(data.get("limit", 5))
    filter_persona = data.get("filter_persona", "").strip()
    filter_type = data.get("intent_type", "").strip()
    filter_allow = data.get("allow", None)

    # ✅ 权限判断
    if not has_log_access(persona):
        return JSONResponse({
            "status": "fail",
            "reply": "🚫 当前身份无权查询日志。",
            "logs": []
        })

    # ✅ 查询调用
    logs = query_logs(
        persona=filter_persona if filter_persona else None,
        intent_type=filter_type if filter_type else None,
        allow=filter_allow,
        limit=limit
    )

    # ✅ 精简字段输出
    simplified_logs = [
        {
            "timestamp": log["timestamp"],
            "persona": log["persona"],
            "message": log["message"],
            "intent_type": log.get("intent_type", ""),
            "allow": log.get("allow", False),
            "reason": log.get("reason", "")
        } for log in logs
    ]

    return JSONResponse({
        "status": "success",
        "reply": f"✅ 共返回 {len(simplified_logs)} 条日志记录：",
        "logs": simplified_logs
    })
