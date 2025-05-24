import os
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client

# ✅ 环境加载与 Supabase 初始化
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ FastAPI & 模板初始化
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 指令入口 /chat
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        if skip_parsing and "intent" in data:
            intent = data["intent"]
        else:
            intent = parse_intent(message, persona)

        intent["persona"] = persona
        intent["source"] = message

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

# ✅ 日志查询接口
@app.post("/log/query")
async def query_log(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    secret = data.get("secret", "").strip()
    limit = int(data.get("limit", 5))
    filter_persona = data.get("filter_persona", "").strip()
    filter_type = data.get("intent_type", "").strip()
    filter_allow = data.get("allow", None)

    if not check_secret_permission(persona, secret):
        return JSONResponse({
            "status": "fail",
            "reply": "🚫 身份或密钥错误，无权查询日志。",
            "logs": []
        })

    logs = query_logs(
        persona=filter_persona if filter_persona else None,
        intent_type=filter_type if filter_type else None,
        allow=filter_allow,
        limit=limit
    )

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

# ✅ 将军专属控制台视图：登录页
@app.get("/dashboard")
async def dashboard_login(request: Request):
    return templates.TemplateResponse("dashboard_login.html", {"request": request})

# ✅ 控制台处理逻辑：身份验证 + 数据读取
@app.post("/dashboard")
async def dashboard_panel(request: Request):
    form = await request.form()
    persona = form.get("persona", "").strip()
    secret = form.get("secret", "").strip()

    if not check_secret_permission(persona, secret) or persona != "将军":
        return templates.TemplateResponse("dashboard_login.html", {
            "request": request,
            "error": "身份验证失败"
        })

    result = supabase.table("persona_keys").select("*").order("created_at", desc=True).execute()
    personas = result.data if result and result.data else []

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "personas": personas,
        "persona": persona
    })
