import json
from datetime import datetime
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log_to_supabase(query, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    try:
        if isinstance(reply, str):
            try:
                reply = json.loads(reply)
            except Exception:
                reply = {"text": reply}

        supabase.table("logs").insert({
            "query": query,
            "reply": json.dumps(reply, ensure_ascii=False),
            "intent_result": intent_result,
            "status": status,
            "source": source,
            "persona": intent_result.get("persona") if isinstance(intent_result, dict) else "未知",
            "intent_type": intent_result.get("intent_type") if isinstance(intent_result, dict) else "unknown",
            "message": intent_result.get("message") if isinstance(intent_result, dict) else "(无内容)",
            "raw_intent": raw_intent or json.dumps(intent_result, ensure_ascii=False),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }).execute()
    except Exception as e:
        print("❌ 日志写入失败：", e)
# ✅ 查询日志
def query_logs(filters=None):
    try:
        q = supabase.table(SUPABASE_TABLE).select("*").order("timestamp", desc=True).limit(100)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        result = q.execute()
        return result.data
    except Exception as e:
        print("❌ 查询日志失败：", e)
        return []
