from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase
from supabase import create_client, Client

# ✅ Supabase 初始化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("chat.html", {"request": request})

    try:
        body = await request.json()
        message = body.get("message", "")
        persona = body.get("persona", "将军")

        # 判断是否跳过语义解析
        skip_parsing = body.get("intent_type") == "text"

        # 调用 GPT 意图解析（或跳过）
        intent = parse_intent(message, persona) if not skip_parsing else {
            "intent_type": "text",
            "message": message
        }

        # 权限校验（如 intent 需要授权）
        allowed, reason = check_secret_permission(intent, persona)
        result = None

        if allowed:
            result = intent_dispatcher(intent)
            write_log_to_supabase(persona, intent, "allowed", result)
            return JSONResponse(content={"result": result})
        else:
            result = {"status": "rejected", "reason": reason}
            write_log_to_supabase(persona, intent, "denied", result)
            return JSONResponse(content={"error": reason}, status_code=403)

    except Exception as e:
        write_log_to_supabase("系统", {}, "error", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
