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

# ✅ 导入自定义模块
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona, register_persona

# ✅ 初始化 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 初始化 FastAPI 与模板引擎
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ /chat 聊天主接口
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("chat.html", {"request": request})
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        if not message:
            return JSONResponse(content={"error": "空消息"}, status_code=400)

        intent = data.get("intent") if skip_parsing else parse_intent(message, persona)
        if not check_secret_permission(intent, persona):
            write_log_to_supabase(persona, intent, "denied", "权限不足")
            return JSONResponse(content={"error": "权限不足"}, status_code=403)

        result = intent_dispatcher(intent)
        write_log_to_supabase(persona, intent, "success", result)
        return JSONResponse(content={"result": result})

    except Exception as e:
        write_log_to_supabase("系统", {}, "error", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ 注册角色
@app.post("/persona/register")
async def register_persona_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "").strip()
        secret = data.get("secret", "").strip()
        operator = data.get("operator", "")

        if not check_secret_permission({"intent_type": "authorize"}, operator):
            return JSONResponse(content={"success": False, "error": "权限不足"}, status_code=403)

        if not persona or not secret:
            return JSONResponse(content={"success": False, "error": "名称和密钥不能为空"}, status_code=400)

        result = register_persona(persona, secret)
        return JSONResponse(content={"success": True, "result": str(result)})

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

# ✅ 获取角色权限（分页）
@app.get("/persona/details")
async def get_persona_details(request: Request):
    try:
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 20))
        start = (page - 1) * per_page
        result = supabase.table("roles").select("*").range(start, start + per_page - 1).execute()
        return {"data": result.data}
    except Exception as e:
        return {"error": str(e), "data": []}

# ✅ 更新角色权限
@app.post("/persona/update_permissions")
async def update_permissions(request: Request):
    try:
        data = await request.json()
        role = data.get("role", "").strip()
        permissions = data.get("permissions", [])

        if not role:
            return JSONResponse(content={"status": "fail", "message": "缺少角色"}, status_code=400)

        supabase.table("roles").update({"permissions": permissions}).eq("role", role).execute()
        return JSONResponse(content={"status": "success", "message": "权限已更新"})

    except Exception as e:
        return JSONResponse(content={"status": "fail", "message": str(e)}, status_code=500)

# ✅ 删除角色
@app.post("/delete_persona")
async def delete_persona_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "")
        operator = data.get("operator", "")

        if not check_secret_permission({"intent_type": "delete_persona"}, operator):
            return JSONResponse(content={"error": "权限不足"}, status_code=403)

        result = delete_persona(persona)
        write_log_to_supabase(operator, {"intent_type": "delete_persona", "target": persona}, "success", result)
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ 查询日志
@app.post("/log/query")
async def query_logs_api(request: Request):
    try:
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
    except Exception as e:
        return JSONResponse(content={"error": str(e), "logs": []})

# ✅ 控制台页面：主页
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ✅ 控制台页面：角色权限
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def dashboard_personas(request: Request):
    persona = request.query_params.get("persona", "")
    if not check_secret_permission({"intent_type": "view_personas"}, persona):
        return HTMLResponse(content="<h3>❌ 权限不足：仅将军可管理角色。</h3>", status_code=403)
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

# ✅ 控制台页面：日志
@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    persona = request.query_params.get("persona", "")
    if not check_secret_permission({"intent_type": "view_logs"}, persona):
        return HTMLResponse(content="<h3>❌ 权限不足：仅将军可访问此页面。</h3>", status_code=403)
    return templates.TemplateResponse("logs.html", {"request": request})
