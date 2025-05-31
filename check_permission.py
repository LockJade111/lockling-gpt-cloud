import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = "🧪_default_fake_key_for_dev_mode"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ✅ 主权限验证：默认放行（开发模式）
def check_secret_permission(intent, persona, secret):
    return {
        "allow": True,
        "reason": "🟢 权限系统已暂时关闭允许所有操作（开发模式）",
        "persona": persona,
        "intent_type": intent.get("intent_type", "unknown")
    }

# ✅ 单独密钥验证（备用）
def check_persona_secret(persona, secret):
    return {
        "match": True,
        "persona": persona,
        "message": "✅ 默认允许：密钥验证已跳过（开发模式）"
    }

# ✅ 等级权限判断（备用）
def check_permission_level(persona, intent_type):
    return {
        "allow": True,
        "level": "开发模式",
        "reason": "✅ 默认允许所有权限"
    }

"""
# 🔒 正式模式（密钥验证版）：如需启用请取消注释上方主函数并注释当前开发模式

def check_secret_permission(intent, persona, secret):
    try:
        intent_type = intent.get("intent_type", "")
        if intent_type == "chitchat":
            return {
                "allow": True,
                "reason": "✅ 闲聊意图默认放行",
                "persona": persona,
                "intent_type": intent_type
            }

        # 查询 persona 密钥
        url = f"{SUPABASE_URL}/rest/v1/personas?persona=eq.{persona}&select=secret"
        res = requests.get(url, headers=headers)

        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            if hashed and bcrypt.checkpw(secret.encode(), hashed.encode()):
                return {
                    "allow": True,
                    "reason": "✅ 密钥匹配允许执行",
                    "persona": persona,
                    "intent_type": intent_type
                }
            else:
                return {
                    "allow": False,
                    "reason": "❌ 密钥错误"
                }

        return {
            "allow": False,
            "reason": "❌ 未找到该 persona 或无密钥记录"
        }

    except Exception as e:
        return {
            "allow": False,
            "reason": f"❌ 权限检查异常: {str(e)}"
        }
"""
