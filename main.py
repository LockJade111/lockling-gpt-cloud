from fastapi import Request
from fastapi.responses import JSONResponse

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
            result = await intent_dispatcher.dispatch(intent)
        else:
            result = {"status": "rejected", "reason": reason}

        # 写日志
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
