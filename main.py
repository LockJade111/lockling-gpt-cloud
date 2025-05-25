from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from parse_intent_with_gpt import parse_intent
from check_permission import check_secret_permission
from intent_dispatcher import dispatcher as intent_dispatcher
from supabase_logger import write_log_to_supabase

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.api_route("/chat", methods=["GET", "POST"])
async def chat(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("chat.html", {"request": request})

    try:
        body = await request.json()
        message = body.get("message", "")
        persona = body.get("persona", "将军")
        skip_parsing = body.get("intent_type") == "text"

        # 调用 GPT 解析
        intent = parse_intent(message, persona) if not skip_parsing else {
            "intent_type": "text",
            "message": message
        }

        # 权限判断
        allowed, reason = check_secret_permission(intent, persona)
        result = None

        if allowed:
            result = await intent_dispatcher.dispatch(intent)
        else:
            result = {"status": "rejected", "reason": reason}

        # 日志写入
        await write_log_to_supabase({
            "persona": persona,
            "intent": intent.get("intent_type"),
            "target": intent.get("target", ""),
            "allow": allowed,
            "reason": reason if not allowed else "",
            "reply": result,
            "source": "chat"
        })

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# 可选：本地运行（Render 可忽略）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
