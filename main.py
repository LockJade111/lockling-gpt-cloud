import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 自定义模块导入
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")

# ✅ 初始化 FastAPI
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wrap_result(status: str, reply: str, intent: dict = {}):
    return JSONResponse(content={"status": status, "reply": reply, "intent": intent})

# ✅ 控制台首页跳转
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard/personas")

# ✅ 聊天接口
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "").strip()
        secret = data.get("secret", "").strip()

        if not message or not persona:
            return wrap_result("fail", "❌ 缺少必要参数")

        intent = parse_intent(message, persona)

        if not check_secret_permission(intent, persona, secret):
            write_log_to_supabase(persona, intent, "denied", "权限不足")
            return wrap_result("fail", "⛔️ 权限不足", intent)

        result = intent_dispatcher(intent)
        write_log_to_supabase(persona, intent, "success", result)
        return wrap_result("success", result, intent)

    except Exception as e:
        return wrap_result("fail", f"❌ 系统错误：{str(e)}")

# ✅ chat-ui 测试页面
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat_ui.html", {"request": request})

# ✅ 日志页面
@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# ✅ 日志查询接口
@app.post("/log/query")
async def query_logs_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "")
        secret = data.get("secret", "")

        if not check_secret_permission({"intent_type": "view_logs"}, persona, secret):
            return JSONResponse(content={"logs": [], "error": "无权限"}, status_code=403)

        logs = query_logs(persona=persona)
        return JSONResponse(content={"logs": logs})

    except Exception as e:
        return JSONResponse(content={"logs": [], "error": str(e)})

# ✅ 角色管理页面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def dashboard_personas(request: Request):
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

# ✅ 注册新角色
@app.post("/persona/register")
async def register_api(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    secret = data.get("secret", "").strip()
    operator = data.get("operator", "")

    if not check_secret_permission({"intent_type": "register"}, operator, SUPER_SECRET_KEY):
        return JSONResponse(content={"success": False, "error": "权限不足"})

    try:
        result = register_persona(persona, secret)
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 删除角色
@app.post("/persona/delete")
async def delete_api(request: Request):
    data = await request.json()
    persona = data.get("persona", "")
    operator = data.get("operator", "")

    if not check_secret_permission({"intent_type": "delete"}, operator, SUPER_SECRET_KEY):
        return JSONResponse(content={"success": False, "error": "权限不足"})

    try:
        result = delete_persona(persona)
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})
