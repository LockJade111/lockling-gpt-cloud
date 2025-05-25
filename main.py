import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# ✅ 加载 .env 配置
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")

# ✅ 初始化 supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 初始化 FastAPI 应用
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 设置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 统一输出结构
def wrap_result(status: str, reply: str, intent: dict = {}):
    return JSONResponse(content={"status": status, "reply": reply, "intent": intent})


# ✅ 控制台首页重定向
@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/dashboard/personas")


# ✅ Persona 控制台页面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def show_persona_dashboard(request: Request):
    response = supabase.table("personas").select("*").execute()
    personas = response.data if response else []
    return templates.TemplateResponse("dashboard_personas.html", {"request": request, "personas": personas})


# ✅ 注册新 persona
@app.post("/persona/register")
async def register_persona_route(
    name: str = Form(...),
    persona: str = Form(...),
    permissions: str = Form(...),
):
    result = register_persona(supabase, name, persona, permissions, SUPER_SECRET_KEY)
    return wrap_result("success", "注册成功", {}) if result else wrap_result("error", "注册失败")


# ✅ 删除 persona
@app.post("/persona/delete")
async def delete_persona_route(
    persona: str = Form(...),
    secret: str = Form(...),
):
    result = delete_persona(supabase, persona, secret, SUPER_SECRET_KEY)
    return wrap_result("success", "删除成功", {}) if result else wrap_result("error", "删除失败")


# ✅ 日志列表
@app.get("/dashboard/logs", response_class=HTMLResponse)
async def show_logs(request: Request):
    logs = query_logs(supabase, limit=100)
    return templates.TemplateResponse("dashboard_logs.html", {"request": request, "logs": logs})


# ✅ 测试对话口
@app.get("/chat_test", response_class=HTMLResponse)
async def test_chat_ui(request: Request):
    return templates.TemplateResponse("chat_test.html", {"request": request})


# ✅ 接收对话消息
@app.post("/chat")
async def chat_endpoint(
    prompt: str = Form(...),
    secret: str = Form(...),
):
    if not check_secret_permission(secret, SUPER_SECRET_KEY):
        return wrap_result("error", "❌ 权限密钥无效")

    intent = parse_intent(prompt)
    reply = intent_dispatcher(intent)
    write_log_to_supabase(supabase, prompt, reply, intent)
    return wrap_result("success", reply, intent)
