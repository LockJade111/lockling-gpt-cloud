import os
import requests
import bcrypt
import json
from dotenv import load_dotenv
from pathlib import Path

# ✅ 强化版 dotenv 加载
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# ✅ 读取环境变量
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY")
if not SUPER_SECRET_KEY:
    raise ValueError("🚨 缺少 SUPER_SECRET_KEY，权限系统无法初始化。请检查 .env 设置。")

# ✅ Supabase 请求头
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ✅ 单次密钥验证（bcrypt 比对）
def check_persona_secret(requestor: str, secret: str) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/persona_keys?persona=eq.{requestor}&select=secret_hash"
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret_hash")
            return hashed and bcrypt.checkpw(secret.encode(), hashed.encode())
        return False
    except Exception as e:
        print("❌ check_persona_secret 出错:", e)
        return False

# ✅ 意图权限验证（角色是否允许该行为）
def is_intent_authorized(requestor: str, intent_type: str) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/persona_roles?requestor=eq.{requestor}&intent=eq.{intent_type}"
        res = requests.get(url, headers=headers)
        return res.status_code == 200 and bool(res.json())
    except Exception as e:
        print("❌ intent 权限验证失败:", e)
        return False

# ✅ 更新密钥（支持初设或更改）
def update_persona_secret(requestor: str, new_secret: str) -> bool:
    try:
        hashed = bcrypt.hashpw(new_secret.encode(), bcrypt.gensalt()).decode()
        url = f"{SUPABASE_URL}/rest/v1/persona_keys?requestor=eq.{requestor}"
        payload = json.dumps({"secret": hashed})
        res = requests.patch(url, headers=headers, data=payload)
        return res.status_code in [200, 204]
    except Exception as e:
        print("❌ update_persona_secret 出错:", e)
        return False

# ✅ 核心权限验证入口（身份 + 密钥 + 行为）
def check_secret_permission(intent: dict, persona: str, secret: str) -> dict:
    try:
        requestor = persona or intent.get("requestor", "")
        intent_type = intent.get("intent_type", "unknown")
        secret = secret or intent.get("secret", "")

        result = {
            "allow": False,
            "reason": "❌ 默认拒绝",
            "requestor": requestor,
            "intent_type": intent_type
        }

        # ✅ 无需权限检查的意图类型
        if intent_type in ["chitchat", "register_persona", "confirm_secret"]:
            result["allow"] = True
            result["reason"] = f"🟡 {intent_type} 意图跳过权限校验"
            return result

        # ❌ 缺关键字段
        if not requestor or not secret:
            result["reason"] = "❌ 缺少身份（persona）或密钥（secret）字段"
            return result

        # ✅ 管理员超级密钥快速通行
        if requestor == "将军" and secret == SUPER_SECRET_KEY:
            result["allow"] = True
            result["reason"] = "✅ 超级身份确认，权限放行"
            return result

        # ✅ 进行 Supabase 密钥匹配
        if check_persona_secret(requestor, secret):
            if is_intent_authorized(requestor, intent_type):
                result["allow"] = True
                result["reason"] = f"✅ 密钥验证通过且授权执行 {intent_type}"
            else:
                result["reason"] = f"❌ 密钥正确但无权执行 {intent_type}"
        else:
            result["reason"] = "❌ 密钥验证失败"

        return result

    except Exception as e:
        print("❌ 权限验证异常:", e)
        return {
            "allow": False,
            "reason": f"❌ 异常错误：{str(e)}",
            "requestor": intent.get("requestor", "unknown"),
            "intent_type": intent.get("intent_type", "unknown")
        }
