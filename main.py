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

# ✅ 标准返回封装
def wrap_result(status: str, reply: str, intent: dict = {}):
    return {"status": status, "reply": reply, "intent": intent}

# ✅ /chat 主接口（GPT 指令分发入口）
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
            return JSONResponse(content=wrap_result("fail", "⚠️ 空消息无法处理"), status_code=400)

        intent = data.get("intent") if skip_parsing else parse_intent(message, persona)
        if not intent or not isinstance(intent, dict):
            return JSONResponse(content=wrap_result("fail", "❓ 无法识别的意图结构"), status_code=400)

        if not check_secret_permission(intent, persona):
            reply = "❌ 当前身份无权限执行此操作"
            write_log_to_supabase(persona, intent, "denied", reply)
            return JSONResponse(content=wrap_result("fail", reply, intent), status_code=403)

        result = intent_dispatcher(intent)
        write_log_to_supabase(persona, intent, "success", result)
        return JSONResponse(content=wrap_result("success", result, intent))

    except Exception as e:
        write_log_to_supabase("系统", {}, "error", str(e))
        return JSONResponse(content=wrap_result("fail", f"❌ 系统异常：{str(e)}"), status_code=500)

# ✅ 注册角色
@app.post("/persona/register")
async def register_persona_api(request: Request):
    data = await request.json()
    persona = data.get("persona", "").strip()
    secret = data.get("secret", "").strip()
    operator = data.get("operator", "将军")

    if not check_secret_permission({"intent_type": "authorize"}, operator):
        return JSONResponse(content={"success": False, "error": "权限不足"}, status_code=403)

    if not persona or not secret:
        return JSONResponse(content={"success": False, "error": "名称和密钥不能为空"}, status_code=400)

    try:
        result = register_persona(persona, secret)
        return JSONResponse(content={"success": True, "result": result.data if hasattr(result, 'data') else str(result)})
    except Exception as e:
        if "already exists" in str(e):
            return JSONResponse(content={"success": False, "error": "该角色已存在"}, status_code=400)
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 查询角色权限详情
@app.get("/persona/details")
async def get_persona_details():
    try:
        result = supabase.table("roles").select("role, permissions").execute()
        return {"data": result.data}
    except Exception as e:
        return {"error": str(e), "data": []}

# ✅ 更新角色权限
@app.post("/persona/update_permissions")
async def update_permissions(request: Request):
    data = await request.json()
    role = data.get("role", "").strip()
    permissions = data.get("permissions", [])

    if not role:
        return JSONResponse(content={"status": "fail", "message": "缺少角色"}, status_code=400)

    try:
        supabase.table("roles").update({"permissions": permissions}).eq("role", role).execute()
        return JSONResponse(content={"status": "success", "message": "权限已更新"})
    except Exception as e:
        return JSONResponse(content={"status": "fail", "message": str(e)}, status_code=500)

# ✅ 删除角色接口
@app.post("/delete_persona")
async def delete_persona_api(request: Request):
    data = await request.json()
    persona = data.get("persona", "")
    operator = data.get("operator", "")

    if not check_secret_permission({"intent_type": "delete_persona"}, operator):
        return JSONResponse(content={"error": "权限不足"}, status_code=403)

    result = delete_persona(persona)
    write_log_to_supabase(operator, {"intent_type": "delete_persona", "target": persona}, "success", result)
    return JSONResponse(content={"result": result})

# ✅ 查询日志
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

# ✅ 管理界面页面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def dashboard_personas(request: Request):
    persona = request.query_params.get("persona", "")
    if not check_secret_permission({"intent_type": "view_personas"}, persona):
        return HTMLResponse(content="<h3>❌ 权限不足：仅将军可管理角色。</h3>", status_code=403)
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    persona = request.query_params.get("persona", "")
    if not check_secret_permission({"intent_type": "view_logs"}, persona):
        return HTMLResponse(content="<h3>❌ 权限不足：仅将军可访问此页面。</h3>", status_code=403)
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
