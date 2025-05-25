import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ 自定义模块导入
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# ✅ 初始化 Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 初始化 FastAPI 与模板
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 统一返回结构
def wrap_result(status: str, reply: str, intent: dict = {}):
    return {"status": status, "reply": reply, "intent": intent}

# ✅ GPT 主接口
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    try:
        data = await request.json() if request.method == "POST" else dict(request.query_params)
        message = data.get("message", "").strip()
        persona = data.get("persona", "").strip() or "访客"
        skip_parsing = data.get("skip_parsing", False)

        if not message:
            return JSONResponse(content=wrap_result("fail", "❌ 空消息"), status_code=400)

        intent = data.get("intent") if skip_parsing else parse_intent(message, persona)
        if not check_secret_permission(intent, persona):
            return JSONResponse(content=wrap_result("fail", "🔒 权限不足", intent), status_code=403)

        result = intent_dispatcher(intent)
        return JSONResponse(content=wrap_result("success", result, intent))

    except Exception as e:
        return JSONResponse(content=wrap_result("error", str(e)), status_code=500)

# ✅ 注册角色接口
@app.post("/persona/register")
async def register_persona_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "").strip()
        secret = data.get("secret", "").strip()
        operator = data.get("operator", "").strip()

        if not check_secret_permission({"intent_type": "authorize"}, operator):
            return JSONResponse(content={"success": False, "error": "❌ 权限不足"}, status_code=403)

        result = register_persona(persona, secret)
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 更新权限接口
@app.post("/persona/update_permissions")
async def update_permissions(request: Request):
    try:
        data = await request.json()
        role = data.get("role", "")
        permissions = data.get("permissions", [])

        if not role:
            return JSONResponse(content={"success": False, "error": "❌ 缺少角色名"}, status_code=400)

        supabase.table("roles").update({"permissions": permissions}).eq("role", role).execute()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 删除角色接口
@app.post("/delete_persona")
async def delete_persona_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "")
        operator = data.get("operator", "")

        if not check_secret_permission({"intent_type": "delete_persona"}, operator):
            return JSONResponse(content={"success": False, "error": "❌ 权限不足"}, status_code=403)

        result = delete_persona(persona)
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 页面路由
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/personas")
async def dashboard_personas(request: Request):
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

# ✅ 分页日志接口（供前端加载）
@app.post("/log/query")
async def query_logs_api(request: Request):
    try:
        data = await request.json()
        filters = {
            "persona": data.get("persona"),
            "intent_type": data.get("intent_type"),
            "allow": data.get("allow"),
        }
        limit = data.get("limit", 20)
        offset = data.get("offset", 0)

        logs = query_logs(filters, limit=limit, offset=offset)
        return JSONResponse(content={"logs": logs})
    except Exception as e:
        return JSONResponse(content={"logs": [], "error": str(e)})
