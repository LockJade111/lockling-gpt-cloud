import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "logs")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 写入日志（结构清晰 + 安全性字段）
def write_log_to_supabase(persona: str, intent_result: dict, status: str, reply: str):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "persona": persona,
            "message": intent_result.get("message", ""),
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False) if isinstance(intent_result.get("allow"), bool) else None,
            "reason": intent_result.get("reason", ""),
            "reply": reply,
            "source": intent_result.get("source", ""),
            "status": status,
            "env": os.getenv("NODE_ENV", "local"),
            "allow": intent_result.get("allow", False) if isinstance(intent_result.get("allow"), bool) else False,
        }

        response = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志写入成功")
        return response
    except Exception as e:
        print(f"❌ 写入日志失败: {e}")
        return None

# ✅ 查询日志（支持筛选 + 分页）
def query_logs(filters: dict = {}, limit: int = 25, offset: int = 0):
    try:
        query = supabase.table(SUPABASE_TABLE).select("*").order("timestamp", desc=True)

        if filters.get("persona"):
            query = query.eq("persona", filters["persona"])
        if filters.get("intent_type"):
            query = query.eq("intent_type", filters["intent_type"])
        if filters.get("allow") is not None:
            query = query.eq("allow", filters["allow"])

        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []

    except Exception as e:
        print(f"❌ 查询日志失败: {e}")
        return []
