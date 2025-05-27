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
        # 保证 reply 是对象
        if isinstance(reply, str):
            try:
                reply = json.loads(reply)
            except:
                reply = {"text": reply}

        # ✅ intent_result 不能是字符串，要确保是 dict
        if isinstance(intent_result, str):
            try:
                intent_result = json.loads(intent_result)
            except:
                intent_result = {"raw": intent_result}

        supabase.table("logs").insert({
            "query": query,
            "reply": reply,
            "intent_result": intent_result,
            "status": status,
            "source": source,
            "persona": intent_result.get("persona") if isinstance(intent_result, dict) else "未知",
            "intent_type": intent_result.get("intent_type") if isinstance(intent_result, dict) else "unknown",
            "message": intent_result.get("message") if isinstance(intent_result, dict) else "(无内容)",
            "raw_intent": raw_intent or intent_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }).execute()
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
