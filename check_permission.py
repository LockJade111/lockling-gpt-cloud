import os
import requests
import bcrypt
from dotenv import load_dotenv
import json

load_dotenv()

# ========== 常量读取 ==========
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPER_SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "玉衡在手")

# Supabase 请求头
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ✅ 校验某 requestor 密钥是否匹配
def check_persona_secret(requestor: str, secret: str) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/persona_keys?requestor=eq.{requestor}&select=secret"
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            return hashed and bcrypt.checkpw(secret.encode(), hashed.encode())
        return False
    except Exception as e:
        print("❌ check_persona_secret 出错:", e)
        return False

# ✅ 检查某 requestor 是否具备 intent 权限
def is_intent_authorized(requestor: str, intent: str) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/persona_roles?requestor=eq.{requestor}&intent=eq.{intent}"
        res = requests.get(url, headers=headers)
        return bool(res.status_code == 200 and res.json())
    except Exception as e:
        print("❌ intent 权限验证失败:", e)
        return False

# ✅ 更新某 requestor 的密钥（用于设置或更换密钥）
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

# ✅ 核心验证函数密钥与权限全流程校验

def check_secret_permission(intent: dict, persona: str, secret: str) -> dict:
    # 你已有的权限判断逻辑
    ...
    try:
        requestor = intent.get("requestor", "")
        secret = intent.get("secret", "")
        intent_type = intent.get("intent_type", "unknown")

        result = {
            "allow": False,
            "reason": "❌ 默认拒绝未通过验证",
            "requestor": requestor,
            "intent_type": intent_type
        }

        if not requestor or not secret:
            result["reason"] = "❌ 缺少 requestor 或密钥字段"
            return result

        # ---------- 超级密钥（将军身份）立即放行 ----------
        if requestor == "将军" and secret == SUPER_SECRET_KEY:
            result["allow"] = True
            result["reason"] = "✅ 管理员身份确认权限放行"
            return result

        # ---------- bcrypt 密钥比对 ----------
        url = f"{SUPABASE_URL}/rest/v1/persona_keys?requestor=eq.{requestor}&select=secret"
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json():
            hashed = res.json()[0].get("secret")
            if hashed and bcrypt.checkpw(secret.encode(), hashed.encode()):
                if is_intent_authorized(requestor, intent_type):
                    result["allow"] = True
                    result["reason"] = f"✅ 密钥正确且有权执行{intent_type}"
                else:
                    result["reason"] = f"❌ 密钥正确但无权执行{intent_type}"
                return result

        result["reason"] = "❌ 密钥验证失败或权限未授权"
        return result

    except Exception as e:
        print("❌ 权限校验异常:", e)
        return {
            "allow": False,
            "reason": f"❌ 异常错误{str(e)}",
            "requestor": intent.get("requestor", "unknown"),
            "intent_type": intent.get("intent_type", "unknown")
        }
