import os
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# ✅ 智能写入桥函数（放在 main.py 顶部 write_log 导入下方）
from src.supabase_logger import write_log_to_supabase
from src.local_logger import write_log_to_local
def write_log_bridge(message, result, intent, status):
    """
    根据意图或数据内容判断写入 Supabase 还是本地
    """
    try:
        # 若未声明 sensitive，默认走 Supabase 写入
        sensitive = intent.get("sensitive", False)
        if sensitive:
            write_log_to_local(message, result, intent, status)
        else:
            write_log_to_supabase(message, result, intent, status)
    except Exception as e:
        print(f"⚠️ 日志写入失败：{e}")

# ✅ 内部模块导入
from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from persona_keys import delete_persona
from src.register_new_persona import register_new_persona
from src.logger_bridge import write_log

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")

# ✅ FastAPI 初始化
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 统一返回格式
def wrap_result(status: str, reply: str, intent: dict = {}):
    return JSONResponse(content={"status": status, "reply": reply, "intent": intent})

# ✅ 首页重定向
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard/personas")

# ✅ 聊天主接口
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        persona = data.get("persona", "").strip()
        secret = data.get("secret", "").strip()

        if not message or not persona:
            return wrap_result("fail", "❌ 缺少输入内容")

        intent = parse_intent(message, persona, secret)        

        if not check_secret_permission(intent, persona, secret):
            write_log_bridge(message, "权限不足", intent, "denied")
            return wrap_result("fail", "⛔️ 权限不足", intent)

        result = intent_dispatcher(intent)
        write_log_bridge(message, result, intent, "success")
        return wrap_result("success", result, intent)
        
        
    except Exception as e:
        traceback.print_exc()
        return wrap_result("fail", f"系统错误：{str(e)}")

# ✅ 日志查询接口（权限判断 + 异常处理合并）
@app.post("/log/query")
async def query_logs_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "")
        secret = data.get("secret", "")

        if not check_secret_permission({"intent_type": "view_logs"}, persona, secret):
            return JSONResponse(content={"logs": [], "error": "权限不足"}, status_code=403)

        filters = {"persona": persona} if persona else {}
        logs = query_logs(filters=filters)
        print("✅ logs 输出：", logs[:1])
        return JSONResponse(content={"logs": logs})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"logs": [], "error": str(e)})

# ✅ 聊天测试页面（绑定到 chatbox.html）
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chatbox.html", {"request": request})

# ✅ 角色管理界面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def dashboard_personas(request: Request):
    return templates.TemplateResponse("dashboard_personas.html", {"request": request})

# ✅ 注册角色接口
@app.post("/persona/register")
def register_persona(
    name: str = Form(...),
    persona: str = Form(...),
    secret: str = Form(...),
    intro: str = Form(""),
    authorize: str = Form("")
):
    try:
        result = register_new_persona(
            name=name,
            persona=persona,
            secret=secret,
            intro=intro,
            authorize=authorize
        )
        return result
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"注册失败：{str(e)}"}

# ✅ 删除角色接口
@app.post("/persona/delete")
async def delete_api(request: Request):
    try:
        data = await request.json()
        persona = data.get("persona", "")
        operator = data.get("operator", "")

        if not check_secret_permission({"intent_type": "delete"}, operator, SUPER_SECRET_KEY):
            return JSONResponse(content={"success": False, "error": "权限不足"})

        result = delete_persona(persona)
        return JSONResponse(content={"success": True, "result": result})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"success": False, "error": str(e)})

# ✅ 日志展示页面
@app.get("/logs", response_class=HTMLResponse)
async def get_logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# ✅ 启动服务（用于本地或 Render 云端）
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
