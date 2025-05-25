import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ✅ 环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")

# ✅ 自定义模块
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# ✅ Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ FastAPI 初始化
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

# ✅ 统一输出结构
def wrap_result(status: str, reply: str, intent: dict = {}):
    return {"status": status, "reply": reply, "intent": intent}


# ✅ 主页路由（可选）
@app.get("/")
async def home(request: Request):
    return RedirectResponse(url="/dashboard/personas")


# ✅ 管理界面：角色列表页面
@app.get("/dashboard/personas")
async def dashboard_personas(request: Request):
    result = supabase.table("personas").select("*").execute()
    data = result.data if result.data else []
    return templates.TemplateResponse("dashboard_personas.html", {
        "request": request,
        "personas": data
    })


# ✅ 注册新角色
@app.post("/persona/register")
async def register_persona_route(
    name: str = Form(...),
    persona: str = Form(...),
    secret: str = Form(...)
):
    if not check_secret_permission(secret, required_permission="创建角色"):
        return RedirectResponse(url="/dashboard/personas", status_code=303)
    register_persona(name, persona)
    return RedirectResponse(url="/dashboard/personas", status_code=303)


# ✅ 删除角色
@app.post("/persona/delete")
async def delete_persona_route(
    request: Request,
    id: str = Form(...),
    secret: str = Form(default="")
):
    if not check_secret_permission(secret, required_permission="创建角色"):
        return RedirectResponse(url="/dashboard/personas", status_code=303)
    delete_persona(id)
    return RedirectResponse(url="/dashboard/personas", status_code=303)


# ✅ GPT 主聊天接口
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    data = await request.json()
    intent = parse_intent(data.get("text", ""))
    intent_result = intent_dispatcher(intent, supabase)
    write_log_to_supabase(intent_result)
    return wrap_result(**intent_result)


# ✅ 日志查询（可选）
@app.get("/logs")
async def logs(request: Request, persona: str = ""):
    records = query_logs(persona)
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": records,
        "persona": persona
    })
