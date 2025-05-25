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
def root():
    return RedirectResponse(url="/dashboard/personas")

# ✅ 控制台页面
@app.get("/dashboard/personas", response_class=HTMLResponse)
def dashboard_personas(request: Request):
    data = supabase.table("personas").select("*").execute()
    personas = data.data if data.data else []
    return templates.TemplateResponse("dashboard_personas.html", {"request": request, "personas": personas})

# ✅ 注册新角色
@app.post("/persona/register")
def register_persona_api(name: str = Form(...), persona: str = Form(...), permissions: str = Form(...)):
    try:
        register_persona(name, persona, permissions)
        return RedirectResponse(url="/dashboard/personas", status_code=303)
    except Exception as e:
        return wrap_result("error", f"注册异常：{e}")

# ✅ 删除角色
@app.post("/persona/delete")
def delete_persona_api(persona: str = Form(...), secret: str = Form(...)):
    try:
        if not check_secret_permission(secret):
            return wrap_result("error", "权限不足，拒绝删除")
        delete_persona(persona)
        return RedirectResponse(url="/dashboard/personas", status_code=303)
    except Exception as e:
        return wrap_result("error", f"删除异常：{e}")

# ✅ GPT 对话口（可选）
@app.post("/chat")
def chat_api(prompt: str = Form(...), role: str = Form(...), secret: str = Form(...)):
    try:
        if not check_secret_permission(secret):
            return wrap_result("error", "权限不足，拒绝访问")

        intent = parse_intent(prompt, role)
        reply = intent_dispatcher(intent, supabase)
        write_log_to_supabase(prompt, role, reply, intent)
        return wrap_result("success", reply, intent)
    except Exception as e:
        return wrap_result("error", f"系统异常：{e}")
