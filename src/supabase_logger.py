import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ 环境变量加载
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_LOG_TABLE = os.getenv("SUPABASE_LOG_TABLE", "logs")  # 可自定义表名
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ 环境变量 SUPABASE_URL 或 SUPABASE_KEY 未设置，无法连接 Supabase")

# ✅ 创建客户端（只在变量存在时执行）
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 日志写入函数（稳定结构 + 自动格式化）
def write_log_to_supabase(message, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    try:
        if isinstance(reply, str):
            reply_text = reply
            reply_obj = {"text": reply}
        elif isinstance(reply, dict):
            reply_text = json.dumps(reply, ensure_ascii=False)
            reply_obj = reply
        else:
            reply_text = str(reply)
            reply_obj = {"text": str(reply)}

        # 提取字段
        persona = intent_result.get("persona") if isinstance(intent_result, dict) else "未知"
        intent_type = intent_result.get("intent_type") if isinstance(intent_result, dict) else "unknown"
        raw = raw_intent or json.dumps(intent_result, ensure_ascii=False)

        data = {
            "query": message,
            "reply": reply_text,
            "status": status,
            "source": source,
            "persona": persona,
            "intent_type": intent_type,
            "message": intent_result.get("message") if isinstance(intent_result, dict) else "(无内容)",
            "target": intent_result.get("target") if isinstance(intent_result, dict) else "",
            "raw_intent": raw,
            "intent_result": json.dumps(intent_result, ensure_ascii=False) if intent_result else "{}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        supabase.table("logs").insert(data).execute()

    except Exception as e:
        print("❌ 日志写入失败", e)

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
        print("❌ 查询日志失败", e)
        return []
