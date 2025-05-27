import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_LOG_TABLE", "logs")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 写入日志（兼容 logs.html 渲染结构）
def write_log_to_supabase(query: str, reply, intent_result=None, status: str = "success", source: str = "cloud", raw_intent=None):
    try:
        # 处理 reply 为纯文本或 JSON 字符串
        if isinstance(reply, dict):
            reply_str = json.dumps(reply, ensure_ascii=False)
        elif isinstance(reply, str):
            try:
                parsed = json.loads(reply)
                reply_str = json.dumps(parsed, ensure_ascii=False)
            except:
                reply_str = reply
        else:
            reply_str = str(reply)

        # 处理 intent_result 为 dict
        if isinstance(intent_result, str):
            try:
                intent_result = json.loads(intent_result)
            except:
                intent_result = {}

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "persona": intent_result.get("persona", "未知"),
            "message": intent_result.get("message", query),
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False),
            "reason": intent_result.get("reason", ""),
            "reply": reply_str,
            "source": source,
            "status": status,
            "env": os.getenv("NODE_ENV", "local"),
            "intent_result":intent_result,
            "raw_intent": raw_intent or intent_result,
        }

        supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志写入成功")

    except Exception as e:
        print("❌ 日志写入失败:", e)

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
