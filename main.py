import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ✅ 模块加载
import intent_dispatcher
import check_permission
from semantic_parser import parse_intent  # ✅ 引入语义解析模块
from supabase_logger import write_log_to_supabase  # ✅ 如你已有日志模块

# ✅ 加载环境变量
load_dotenv()

app = FastAPI()

# ✅ CORS 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 权限判断函数
def has_permission(persona, required):
    if not required:
        return True
    try:
        permissions = check_permission.get_persona_permissions(persona)
        return required in permissions
    except Exception as e:
        print(f"❌ 权限加载失败：{e}")
        return False

# ✅ 主入口路由
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    message = data.get("message", "").strip()
    persona = data.get("persona", "Lockling 锁灵").strip()
    explicit_intent = data.get("intent")
    skip_parsing = data.get("skip_parsing", False)

    if not message:
        return {"status": "fail", "reply": "❌ 消息不能为空。"}

    # ✅ 优先使用显式 intent，否则解析
    try:
        if explicit_intent:
            intent_result = explicit_intent
        else:
            intent_result = parse_intent(message, persona)

        print(f"🧠 调试中: intent_result = {intent_result}")
    except Exception as e:
        print(f"❌ 无法解析意图: {e}")
        return {"status": "fail", "reply": "❌ 意图解析失败，请检查语句或配置。"}

    intent_type = intent_result.get("intent_type")
    required_permission = intent_result.get("requires", "")

    print(f"🧠 调试中: intent_type={intent_type} | requires={required_permission} | persona={persona}")

    # ✅ 权限校验
    if not has_permission(persona, required_permission):
        print("🚫 权限判断未通过")
        return {
            "status": "fail",
            "reply": "🚫 权限不足，拒绝操作。",
            "intent": intent_result,
            "persona": persona
        }

    # ✅ 意图分发处理
    response = intent_dispatcher.dispatch_intents(intent_result, persona)

    # ✅ 日志写入
    try:
        write_log_to_supabase(persona, message, intent_result, response.get("reply", ""))
    except Exception as e:
        print(f"⚠️ 日志写入失败: {e}")

    return {
        "status": "success",
        "reply": response.get("reply", "✅ 操作完成"),
        "intent": response.get("intent", intent_result),
        "persona": persona
    }
