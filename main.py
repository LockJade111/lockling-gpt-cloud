import os
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona

# ✅ 加载 .env 环境变量
load_dotenv(dotenv_path=".env", override=True)

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ FastAPI 应用初始化
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 核心指令入口：解析意图 + 权限校验 + 派发执行
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        # ✅ GPT 语义解析
        intent = data["intent"] if skip_parsing and "intent" in data else parse_intent(message, persona)
        intent["persona"] = persona
        intent["source"] = message

        # ✅ 权限验证
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

        # ✅ 分发执行
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

# ✅ 查询日志接口（用于 Postman 调试）
@app.post("/log/query")
async def query_log(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    secret = data.get("secret", "").strip()
    limit = int(data.get("limit", 50))
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

    simplified = [{
        "timestamp": log["timestamp"],
        "persona": log["persona"],
        "message": log["message"],
        "intent_type": log.get("intent_type", ""),
        "target": log.get("target", ""),
        "allow": log.get("allow", False),
        "reason": log.get("reason", ""),
        "reply": log.get("reply", "")
    } for log in logs]

    return JSONResponse({
        "status": "success",
        "reply": f"✅ 共返回 {len(simplified)} 条日志记录：",
        "logs": simplified
    })

# ✅ 控制台 UI 路由（HTML 可视化）
@app.get("/logs")
def show_logs(request: Request, persona: str = None):
    logs = query_logs(limit=50, persona=persona)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})

# ✅ 删除 persona（仅限将军）
@app.post("/delete_persona")
async def delete_persona_ui(persona: str, request: Request):
    acting_persona = request.cookies.get("persona") or "将军"
    if acting_persona != "将军":
        return JSONResponse({"error": "无权删除角色"}, status_code=403)
    delete_persona(persona)
    return RedirectResponse("/logs", status_code=303)
