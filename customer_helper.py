from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_customer(data: dict) -> str:
    try:
        payload = {
            "name": data.get("name", "未知客户"),
            "phone": data.get("phone", ""),
            "address": data.get("address", ""),
            "service_desc": data.get("service_desc", ""),
            "amount": float(data.get("amount", 0)),
            "created_at": datetime.now().isoformat(),
            "handled_by": data.get("handled_by", "Lockling 锁灵")
        }
        supabase.table("customers").insert(payload).execute()
        return "✅ 客户服务记录已保存"
    except Exception as e:
        return f"❌ 客户信息保存失败: {e}"
