import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# 加载 .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 初始化 FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 首页
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("dashboard_login.html", {"request": request})

# 日志页面
@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# 日志查询 API
@app.post("/logs/query")
async def query_logs_api(request: Request):
    filters = await request.json()
    logs = query_logs(filters, limit=50)
    return {"logs": logs}

# Persona 管理页
@app.get("/dashboard/personas", response_class=HTMLResponse)
def dashboard_personas(request: Request):
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

# ✅ 修复核心接口：/chat 允许 GET + POST
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("chat.html", {"request": request})

    data = await request.json()
    message = data.get("message", "").strip()
    persona = data.get("persona", "将军").strip()
    source = data.get("source", "web")
    skip_parsing = data.get("skip_parsing", False)

    intent = parse_intent(message) if not skip_parsing else {
        "intent_type": "text",
        "message": message
    }
    intent["persona"] = persona
    reply = intent_dispatcher.dispatch(intent)

    write_log_to_supabase({
        "persona": persona,
        "message": message,
        "intent": intent.get("intent_type"),
        "target": intent.get("target_persona"),
        "allow": "yes",
        "reason": "via dispatcher",
        "reply": reply,
        "source": source
    })

    return {
        "persona": persona,
        "message": message,
        "intent": intent,
        "reply": reply
    }

# 注册 persona
@app.post("/persona/register")
async def register_api(request: Request):
    data = await request.json()
    result = register_persona(data)
    return JSONResponse(content=result)

# 删除 persona
@app.post("/persona/delete")
async def delete_api(request: Request):
    data = await request.json()
    result = delete_persona(data.get("persona"))
    return JSONResponse(content=result)
