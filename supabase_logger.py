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

# ✅ 写入日志（结构清晰 + 防乱码 + 类型安全）
def write_log_to_supabase(persona: str, intent_result, status: str, reply):
    try:
        # 若 intent_result 是字符串，先转换为 dict
        if isinstance(intent_result, str):
            try:
                intent_result = json.loads(intent_result)
            except:
                intent_result = {}

        # reply 也处理成字符串，防止嵌套 dict 报错
        if isinstance(reply, dict):
            reply_str = json.dumps(reply, ensure_ascii=False)
        else:
            reply_str = str(reply)

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "persona": persona,
            "message": intent_result.get("query", "无"),
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False),
            "reason": intent_result.get("reason", ""),
            "reply": reply_str,
            "source": intent_result.get("source", ""),
            "status": status,
            "env": os.getenv("NODE_ENV", "local"),

            # 👇将 intent_result 原样作为 JSON 存一份，供前端提取用
            "raw_intent_json": json.dumps(intent_result, ensure_ascii=False)
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
