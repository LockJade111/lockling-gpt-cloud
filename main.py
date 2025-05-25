import os
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# 自定义模块导入
import intent_dispatcher
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from supabase_logger import write_log_to_supabase, query_logs
from supabase import create_client, Client
from persona_keys import delete_persona

# ✅ 加载 .env 环境变量
load_dotenv(dotenv_path=".env", override=True)

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ FastAPI 应用初始化
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 主聊天入口（GPT语义解析）
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "Lockling 锁灵").strip()
        skip_parsing = data.get("skip_parsing", False)

        if not message:
            return JSONResponse(content={"error": "空消息"}, status_code=400)

        if not skip_parsing:
            intent = parse_intent(message, persona)
        else:
            intent = data.get("intent", {})

        permission_passed = check_secret_permission(intent, persona)
        if not permission_passed:
            write_log_to_supabase(persona, intent, "denied", "权限验证失败")
            return JSONResponse(content={"error": "权限不足"}, status_code=403)

        result = intent_dispatcher.dispatch(intent)
        write_log_to_supabase(persona, intent, "success", result)

        return JSONResponse(content={"result": result})

    except Exception as e:
        write_log_to_supabase("系统", {}, "error", f"异常：{str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ 删除 persona 接口
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

# ✅ 查询日志 API
@app.post("/log/query")
async def query_logs_api(request: Request):
    data = await request.json()
    filters = {
        "persona": data.get("persona"),
        "intent_type": data.get("intent_type"),
        "allow": data.get("allow"),
    }
    logs = query_logs(filters)
    return JSONResponse(content={"logs": logs})

# ✅ /logs 页面展示接口
@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})
