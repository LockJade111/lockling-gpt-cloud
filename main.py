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


# ✅ 注册 persona（用于表单注册）
@app.post("/persona/register")
async def register_persona_api(
    name: str = Form(...),
    persona: str = Form(...),
    secret: str = Form(...)
):
    if not check_secret_permission(secret, ["创建角色", "注册"]):
        return wrap_result("fail", "❌ 权限不足，无法注册角色")

    try:
        register_persona(supabase, name, persona)
        return wrap_result("success", f"✅ 角色 {persona} 注册成功")
    except Exception as e:
        return wrap_result("error", f"⚠️ 注册失败：{str(e)}")


# ✅ 删除 persona（用于表单删除）
@app.post("/persona/delete")
async def delete_persona_api(
    persona: str = Form(...),
    secret: str = Form(...)
):
    if not check_secret_permission(secret, ["删除角色"]):
        return wrap_result("fail", "❌ 权限不足，无法删除角色")

    try:
        delete_persona(supabase, persona)
        return wrap_result("success", f"🗑️ 角色 {persona} 删除成功")
    except Exception as e:
        return wrap_result("error", f"⚠️ 删除失败：{str(e)}")


# ✅ 渲染角色列表页面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def show_personas_page(request: Request):
    try:
        result = supabase.table("personas").select("*").execute()
        personas = result.data or []
        return templates.TemplateResponse("dashboard_personas.html", {
            "request": request,
            "personas": personas
        })
    except Exception as e:
        return HTMLResponse(content=f"<h3>❌ 加载失败：{str(e)}</h3>", status_code=500)


# ✅ GPT 聊天主入口
@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    message = data.get("message", "")
    persona = data.get("persona", "")
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return wrap_result("fail", "⛔ 空消息")

    if not skip_parsing:
        intent = parse_intent(message, persona)
    else:
        intent = data.get("intent", {})

    if not check_secret_permission(intent, persona):
        write_log_to_supabase(persona, intent, "denied", "权限不足")
        return wrap_result("fail", "❌ 权限不足")

    result = intent_dispatcher(intent)
    write_log_to_supabase(persona, intent, "success", result)
    return wrap_result("success", result, intent)


# ✅ 查询日志接口
@app.post("/log/query")
async def query_logs_api(request: Request):
    data = await request.json()
    filters = {
        "persona": data.get("persona"),
        "intent_type": data.get("intent_type"),
        "allow": data.get("allow"),
    }
    limit = data.get("limit", 25)
    offset = data.get("offset", 0)
    logs = query_logs(filters, limit=limit, offset=offset)
    return JSONResponse(content={"logs": logs})							
