import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def check_secret_permission(intent, persona, secret):
    """
    三参数权限验证逻辑：
    - 如果 intent_type 是 chitchat，直接放行
    - 否则验证密钥是否匹配（可接入 Supabase 密钥表）
    - 还可拓展权限表查询（persona_roles）进行授权限制
    """
    try:
        intent_type = intent.get("intent_type", "")
        if intent_type == "chitchat":
            return {
                "allow": True,
                "reason": "✅ 闲聊意图默认放行"
            }

        # 查询 persona 密钥
        url = f"{SUPABASE_URL}/rest/v1/personas?persona=eq.{persona}&select=secret"
        res = requests.get(url, headers=headers)

        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            if hashed and bcrypt.checkpw(secret.encode(), hashed.encode()):
                return {
                    "allow": True,
                    "reason": "✅ 密钥匹配，允许执行"
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
            "reason": f"❌ 权限检查异常：{str(e)}"
        }
