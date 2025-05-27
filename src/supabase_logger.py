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
        if isinstance(reply, str):
            try:
                reply = json.loads(reply)
            except Exception:
                reply = {"text": reply}

        # 优化：提取字段默认值
        persona = intent_result.get("persona", "匿名访问者") if isinstance(intent_result, dict) else "匿名访问者"
        intent_type = intent_result.get("intent_type", "未定义指令") if isinstance(intent_result, dict) else "未知"

        # 优化：intent_type 翻译
        intent_label_map = {
            "register": "注册",
            "authorize": "授权",
            "confirm_secret": "确认密钥",
            "confirm_identity": "身份确认",
            "delete": "删除",
            "view_logs": "查看日志",
        }
        translated_intent = intent_label_map.get(intent_type, intent_type)

        # 构造最终写入
        supabase.table("logs").insert({
            "query": query,
            "reply": json.dumps(reply, ensure_ascii=False),
            "intent_result": intent_result,
            "status": status,
            "source": source or "未知来源"
            "persona": persona,
            "intent_type": translated_intent,
            "message": intent_result.get("message") if isinstance(intent_result, dict) else "(无内容)",
            "raw_intent": raw_intent or json.dumps(intent_result, ensure_ascii=False),
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
