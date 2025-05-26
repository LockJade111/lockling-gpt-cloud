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

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")

# ✅ 初始化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wrap_result(status: str, reply: str, intent: dict = {}):
    return JSONResponse(content={"status": status, "reply": reply, "intent": intent})

# ✅ 控制台入口
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard/personas")

# ✅ 聊天接口
@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    persona = form.get("persona")
    message = form.get("message")
    secret = form.get("secret", "")

    if not persona or not message:
        return wrap_result("error", "请输入 persona 和 message")

    if not check_secret_permission(persona, secret, "chat"):
        return wrap_result("error", "权限不足。")

    reply, parsed = parse_intent(persona, message)
    write_log_to_supabase(persona, message, reply)
    return wrap_result("success", reply, parsed)

# ✅ 注册新角色
@app.post("/persona/register")
async def register_persona_route(request: Request):
    form = await request.form()
    name = form.get("name")
    persona = form.get("persona")
    secret = form.get("secret", "")
    return register_persona(supabase, name, persona, secret)

# ✅ 删除角色
@app.post("/persona/delete")
async def delete_persona_route(request: Request):
    form = await request.form()
    persona = form.get("persona")
    secret = form.get("secret", "")
    return delete_persona(supabase, persona, secret)

# ✅ 管理界面
@app.get("/dashboard/personas", response_class=HTMLResponse)
async def dashboard(request: Request):
    result = supabase.table("roles").select("*").execute()
    return templates.TemplateResponse("dashboard_personas.html", {"request": request, "roles": result.data})

# ✅ Chat UI
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui():
    return """
    <html><head><title>Chat 测试界面</title></head>
    <body>
        <h2>💬 Chat UI</h2>
        <form method="post" action="/chat">
            Persona: <input name="persona"><br>
            Message: <input name="message"><br>
            Secret: <input name="secret"><br>
            <button type="submit">发送</button>
        </form>
    </body>
    </html>
    """

# ✅ 日志界面
@app.get("/logs")
async def view_logs(request: Request):
    persona = request.query_params.get("persona")
    secret = request.query_params.get("secret", "")

    if not check_secret_permission(persona, secret, "view_logs"):
        return wrap_result("error", "无权查看日志。")

    logs = query_logs(supabase, persona)
    return logs
