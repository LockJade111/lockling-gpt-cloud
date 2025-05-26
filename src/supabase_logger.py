import os
import json
from datetime import datetime
from supabase import create_client

# 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log_to_supabase(query, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    # 🪛 Debug 输出参数类型
    print("👉 type(query):", type(query))
    print("👉 type(reply):", type(reply))
    print("👉 type(intent_result):", type(intent_result))
    print("👉 type(raw_intent):", type(raw_intent))

    # ✅ 自动解码字符串类型 JSON，防止日志乱码
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except:
            pass

    if isinstance(intent_result, str):
        try:
            intent_result = json.loads(intent_result)
        except:
            pass

    if isinstance(raw_intent, str):
        try:
            raw_intent = json.loads(raw_intent)
        except:
            pass

    # ✅ 格式保障：intent_result 一定是 dict
    if not isinstance(intent_result, dict):
        intent_result = {}

    # ✅ 若 reply 是对象，强制转为 JSON 字符串
    if isinstance(reply, (dict, list)):
        try:
            reply = json.dumps(reply, ensure_ascii=False)
        except:
            reply = str(reply)

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
        print("❌ 日志写入失败：", e)

def query_logs(filters=None):
    try:
        q = supabase.table("logs").select("*").order("timestamp", desc=True).limit(100)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        res = q.execute()
        return res.data
    except Exception as e:
        print("❌ 日志查询失败：", e)
        return []
