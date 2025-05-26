import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# ✅ 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "logs")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except:
        return str(obj)

# ✅ 写入日志
def write_log_to_supabase(query, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    try:
        if isinstance(intent_result, str):
            try:
                intent_result = json.loads(intent_result)
            except:
                intent_result = {}

        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "reply": safe_json(reply),
            "intent_result": safe_json(intent_result),
            "status": status,
            "source": source,
            "persona": intent_result.get("persona", "未知"),
            "intent_type": intent_result.get("intent_type", "unknown"),
            "raw_intent": safe_json(raw_intent or intent_result)
        }

        supabase.table(SUPABASE_TABLE).insert(log).execute()
        print("✅ 日志写入成功")
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
