import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
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

# ✅ 初始化 FastAPI 与模板
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

# ✅ 统一返回结构
def wrap_result(status: str, reply: str, intent: dict = {}):
    return {"status": status, "reply": reply, "intent": intent}

# ✅ GPT 主接口
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        secret = data.get("secret", "")
        print("📥 用户提问：", query)

        if not check_secret_permission(secret):
            raise HTTPException(status_code=403, detail="❌ 权限校验失败")

        intent = parse_intent(query)
        print("🎯 识别意图：", intent)

        reply = intent_dispatcher(intent)
        write_log_to_supabase(query, reply, intent)

        return JSONResponse(wrap_result("success", reply, intent))
    except Exception as e:
        print("❌ 处理失败:", e)
        return JSONResponse(wrap_result("error", f"处理失败：{str(e)}"))

# ✅ 日志接口
@app.get("/logs")
async def get_logs():
    try:
        logs = query_logs()
        return JSONResponse(wrap_result("success", "日志查询成功", {"logs": logs}))
    except Exception as e:
        return JSONResponse(wrap_result("error", f"日志查询失败：{str(e)}"))

# ✅ 渲染角色管理页面
@app.get("/dashboard/personas")
async def dashboard_personas(request: Request):
    try:
        personas = [
            {"id": 1, "name": "Lockling", "role": "智能守护者"},
            {"id": 2, "name": "军师猫", "role": "智囊门神"},
        ]
        offset = 0
        limit = 10
        page = 1
        total = len(personas)

        return templates.TemplateResponse("dashboard_personas.html", {
            "request": request,
            "personas": personas,
            "offset": offset,
            "limit": limit,
            "page": page,
            "total": total
        })
    except Exception as e:
        print("❌ 页面渲染失败：", e)
        return HTMLResponse(content=f"<h1>服务器错误：{e}</h1>", status_code=500)

# ✅ 注册角色接口（修复 undefined 报错）
@app.post("/persona/register")
async def register_new_persona(request: Request):
    try:
        data = await request.json()
        print("📥 注册请求数据：", data)

        name = data.get("name")
        role = data.get("role")
        secret = data.get("secret", "")

        if not name or not role:
            raise ValueError("name 或 role 缺失")

        if not check_secret_permission(secret):
            raise HTTPException(status_code=403, detail="❌ 权限不足")

        result = register_persona(name, role)
        return JSONResponse(wrap_result("success", "角色注册成功", result))
    except Exception as e:
        print("❌ 注册异常：", e)
        return JSONResponse(wrap_result("error", f"注册失败：{str(e)}"))

# ✅ 删除角色接口
@app.post("/persona/delete")
async def delete_existing_persona(request: Request):
    try:
        data = await request.json()
        persona_id = data.get("id")
        secret = data.get("secret", "")
        if not check_secret_permission(secret):
            raise HTTPException(status_code=403, detail="❌ 权限不足")
        result = delete_persona(persona_id)
        return JSONResponse(wrap_result("success", "角色删除成功", result))
    except Exception as e:
        return JSONResponse(wrap_result("error", f"删除失败：{str(e)}"))
