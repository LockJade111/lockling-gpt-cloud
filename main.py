import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ✅ 模块加载
import intent_dispatcher
import check_permission

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 权限判断
def has_permission(persona, required):
    if not required:
        return True
    try:
        permissions = check_permission.get_persona_permissions(persona)
        return required in permissions
    except Exception as e:
        print(f"❌ 权限加载失败：{e}")
        return False

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    message = data.get("message", "").strip()
    persona = data.get("persona", "Lockling 锁灵").strip()
    intent = data.get("intent")
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {
            "status": "fail",
            "reply": "❌ message 为空，无法处理。"
        }

    # ✅ 解析意图
    if not skip_parsing:
        try:
            from semantic_parser import parse_intent  # 若存在语义解析模块
            intent_result = parse_intent(message, persona)
        except Exception as e:
            print(f"❌ 无法解析意图: {e}")
            return {
                "status": "fail",
                "reply": "❌ 意图解析失败，请检查语句或配置。"
            }
    else:
        intent_result = intent or {}

    intent_type = intent_result.get("intent_type", "unknown")
    required = intent_result.get("requires", None)

    print(f"🤖 接收消息: {message} | persona={persona} | intent_type={intent_type} | requires={required}")

    # ✅ 权限校验
    if not has_permission(persona, required):
        print("🔒 权限校验未通过")
        return {
            "status": "fail",
            "reply": f"🔒 权限不足，拒绝操作。",
            "intent": intent_result
        }

    # ✅ 分发处理
    try:
        response = intent_dispatcher.dispatch_intents(intent_result, persona)
    except Exception as e:
        print(f"❌ dispatch_intents 执行出错: {e}")
        return {
            "status": "fail",
            "reply": "❌ dispatch_intents() 执行失败。",
            "intent": intent_result
        }

    # ✅ 写入日志
    try:
        check_permission.write_log_to_supabase(persona, message, intent_result, response)
    except Exception as e:
        print(f"⚠️ 日志写入失败: {e}")

    return {
        "status": "success",
        **response
    }
