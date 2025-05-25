from check_permission import check_secret_permission
from persona_keys import (
    register_persona,
    check_persona_secret,
    revoke_persona,
    delete_persona,
    unlock_persona
)

from dotenv import load_dotenv
import os
from supabase import create_client
from supabase_logger import write_log_to_supabase

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 密钥确认
def handle_confirm_secret(intent):
    print("📥 收到意图：confirm_secret")
    persona = intent.get("persona", "").strip()
    secret = intent.get("secret", "").strip()

    if check_persona_secret(persona, secret):
        return {
            "status": "success",
            "reply": "✅ 密钥验证通过，身份已确认。",
            "intent": intent
        }
    else:
        return {
            "status": "fail",
            "reply": "🚫 密钥错误，身份验证失败。",
            "intent": intent
        }

# ✅ 注册 persona
def handle_register_persona(intent):
    print("📥 收到意图：register_persona")
    persona = intent.get("persona", "").strip()
    new_name = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()

    if not persona or not new_name or not secret:
        return {
            "status": "fail",
            "reply": "❗ 缺少 persona、target 或 secret 字段。",
            "intent": intent
        }

    result = register_persona(persona, new_name, secret)
    return {
        "status": "success" if result else "fail",
        "reply": "✅ 注册成功" if result else "⚠️ 注册失败",
        "intent": intent
    }

# ✅ 删除 persona
def handle_delete_persona(intent):
    print("📥 收到意图：delete_persona")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()
    result = delete_persona(persona, target)
    return {
        "status": "success" if result else "fail",
        "reply": "✅ 删除成功" if result else "⚠️ 删除失败",
        "intent": intent
    }

# ✅ 分发器类
class Dispatcher:
    def __init__(self):
        self.handlers = {
            "confirm_secret": handle_confirm_secret,
            "register_persona": handle_register_persona,
            "delete_persona": handle_delete_persona,
            # 可拓展更多意图
        }

    async def dispatch(self, intent):
        intent_type = intent.get("intent_type")
        handler = self.handlers.get(intent_type)

        if handler:
            return handler(intent)
        else:
            return {
                "status": "fail",
                "reply": f"❓ 未知意图类型：{intent_type}",
                "intent": intent
            }

# ✅ 导出 dispatcher 实例供主程序使用
dispatcher = Dispatcher()
