from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LOG_TABLE = os.getenv("SUPABASE_LOG_TABLE", "logs")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def write_log_to_supabase(message, reply, persona):
    print("🟡 正在尝试写入 Supabase 日志")
    try:
        data = {
            "message": message,
            "reply": reply,
            "persona": persona
        }
        result = supabase.table(LOG_TABLE).insert(data).execute()
        print("✅ 日志写入成功：", result)
    except Exception as e:
        print("❌ 写入 Supabase 日志失败：", e)
