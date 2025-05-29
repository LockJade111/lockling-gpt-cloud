import os
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from generate_reply_with_gpt import generate_reply 

# ✅ 智能写入桥函数（放在 main.py 顶部 write_log 导入下方）
from src.supabase_logger import write_log_to_supabase
from src.local_logger import write_log_to_local
def write_log_bridge(message, result, intent, status):
    """
    根据意图或数据内容判断写入 Supabase 还是本地
    """
    try:
        if SUPABASE_KEY and status == "success":
            write_log_to_supabase(message, result, intent, status)
        else:
            write_log_to_local(message, result, intent, status)
    except Exception as e:
        print("⚠️ 日志写入异常", e)

# ✅ 模块引入（顶部）
from intent_dispatcher import parse_intent        # ✅ 云脑中枢替代旧 intent 模块
from check_permission import check_secret_permission
from generate_reply_with_gpt import generate_reply
from persona_keys import delete_persona
from src.register_new_persona import register_new_persona
from src.logger_bridge import write_log
from src.supabase_logger import write_log_to_supabase
from src.local_logger import write_log_to_local

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
from fastapi.responses import JSONResponse

def wrap_result(status, reply, intent):
    return JSONResponse(content={
        "status": status,
        "reply": reply,
        "intent": intent
    })

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
            return wrap_result("fail", "❌ 缺少输入内容", {})

        # ✅ 意图解析
        intent = parse_intent(message, persona, secret)
        intent["raw_message"] = message

        # ✅ 闲聊直接走 GPT 回复无需权限校验
        if intent.get("intent_type") == "chitchat":
            from generate_reply_with_gpt import generate_reply
            reply_text = generate_reply(message, persona)
            write_log_bridge(message, reply_text, intent, "success")
            return wrap_result("success", reply_text, intent)

        # ✅ 仅对非 chitchat 意图进行权限校验
        if intent.get("intent_type") != "chitchat":
            from check_permission import check_secret_permission
            permission_result = check_secret_permission(intent, persona, secret)
            if not permission_result.get("allow"):
                write_log_bridge(message, permission_result.get("reason", "无权限"), intent, "denied")
                return wrap_result("fail", permission_result.get("reason", "⛔️ 权限不足"), intent)

        # ✅ 非闲聊交给 dispatch
        from intent_dispatcher import intent_dispatcher
        result = intent_dispatcher(intent)

        # ✅ 成功日志记录
        write_log_bridge(message, result, intent, "success")
        return wrap_result("success", result, intent)

    except Exception as e:
        import traceback
        print("❌ 系统错误", traceback.format_exc())
        return wrap_result("fail", "⚠️ 系统错误", {
            "intent_type": "unknown",
            "persona": "",
            "secret": "",
            "target": "",
            "permissions": []
        })

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
        print("✅ logs 输出", logs[:1])
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
        return {"status": "error", "message": f"注册失败{str(e)}"}

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

from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        persona = data.get("persona", "user")  # 默认角色是 user
        secret = data.get("secret", "")        # 可选密钥

        # 🔍 用 GPT 解析意图
        intent = parse_intent(message, persona, secret)

        # 🔧 分发执行
        result = intent_dispatcher(intent)

        # 📋 日志记录
        write_log_bridge(message, result["reply"], intent, result["status"])

        return JSONResponse(content=result)

    except Exception as e:
        print(f"❌ Chat 处理失败{e}")
        return JSONResponse(content={
            "status": "fail",
            "reply": "❌ 出现异常暂时无法处理你的请求",
            "intent": {
                "intent_type": "unknown",
                "persona": "user",
                "secret": "",
                "target": "",
                "permissions": [],
                "allow": False,
                "reason": str(e)
            }
        })

# ✅ 日志展示页面
@app.get("/logs", response_class=HTMLResponse)
async def get_logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# ✅ 启动服务（用于本地或 Render 云端）
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

