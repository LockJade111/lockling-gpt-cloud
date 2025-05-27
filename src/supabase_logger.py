import json
from datetime import datetime
from supabase import create_client
import os

# ✅ 环境变量加载
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_LOG_TABLE = os.getenv("SUPABASE_LOG_TABLE", "logs")  # 可自定义表名
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 日志写入函数（稳定结构 + 自动格式化）
def write_log_to_supabase(query, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    try:
        # 确保 reply 是字典
        if isinstance(reply, str):
            try:
                reply = json.loads(reply)
            except Exception:
                reply = {"text": reply}

        # 写入字段结构（字段缺失自动 fallback）
        log_entry = {
            "query": query or "",
            "reply": reply if isinstance(reply, dict) else {"text": str(reply)},
            "status": status,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "persona": intent_result.get("persona", "") if isinstance(intent_result, dict) else "",
            "intent_type": intent_result.get("intent_type", "") if isinstance(intent_result, dict) else "unknown",
            "message": intent_result.get("message", "") if isinstance(intent_result, dict) else "",
            "target": intent_result.get("target", "") if isinstance(intent_result, dict) else "",
            "allow": intent_result.get("allow", None) if isinstance(intent_result, dict) else None,
            "reason": intent_result.get("reason", "") if isinstance(intent_result, dict) else "",
            "secret": intent_result.get("secret", "") if isinstance(intent_result, dict) else "",
            "env": intent_result.get("env", "") if isinstance(intent_result, dict) else "",
            "permissions": json.dumps(intent_result.get("permissions", []), ensure_ascii=False) if isinstance(intent_result, dict) else "[]",
            "intent_result": intent_result if isinstance(intent_result, dict) else json.loads(intent_result),
            "raw_intent": raw_intent if isinstance(raw_intent, dict) else json.loads(raw_intent),
        }

        supabase.table(SUPABASE_LOG_TABLE).insert(log_entry).execute()

    except Exception as e:
        print("❌ 日志写入失败：", e)

# ✅ 查询日志函数
def query_logs(filters=None):
    try:
        q = supabase.table(SUPABASE_LOG_TABLE).select("*").order("timestamp", desc=True).limit(100)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        result = q.execute()
        return result.data
    except Exception as e:
        print("❌ 查询日志失败：", e)
        return []
