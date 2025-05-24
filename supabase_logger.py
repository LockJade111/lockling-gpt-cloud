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

# ✅ 写入日志
def write_log_to_supabase(message: str, persona: str, intent_result: dict, reply: str):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "persona": persona,
            "message": message,
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False),
            "reason": intent_result.get("reason", ""),
            "reply": reply,
            "source": intent_result.get("source", ""),
            "env": os.getenv("NODE_ENV", "local"),
            "raw_intent": json.dumps(intent_result, ensure_ascii=False)
        }

        response = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志已写入 Supabase")
        return response

    except Exception as e:
        print(f"❌ 写入 Supabase 失败: {e}")
        return None

# ✅ 查询日志（支持多条件筛选）
def query_logs(persona=None, intent_type=None, allow=None, limit=5):
    try:
        query = supabase.table(SUPABASE_TABLE).select("*").order("timestamp", desc=True).limit(limit)
        
        if persona:
            query = query.eq("persona", persona)
        if intent_type:
            query = query.eq("intent_type", intent_type)
        if allow is not None:
            query = query.eq("allow", allow)

        result = query.execute()
        return result.data

    except Exception as e:
        print(f"❌ 日志查询失败: {e}")
        return []
