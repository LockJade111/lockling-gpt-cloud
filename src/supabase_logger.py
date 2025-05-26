import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log_to_supabase(query, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    try:
        supabase.table("logs").insert({
            "query": query,
            "reply": reply,
            "intent_result": intent_result,
            "status": status,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_intent": raw_intent
        }).execute()
    except Exception as e:
        print("日志写入失败：", e)

def query_logs(filters=None):
    try:
        q = supabase.table("logs").select("*").order("timestamp", desc=True).limit(100)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        res = q.execute()
        return res.data
    except Exception as e:
        print("日志查询失败：", e)
        return []
