import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_LOG_TABLE = os.getenv("SUPABASE_LOG_TABLE", "logs")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log_to_supabase(message: str, reply: str, persona: str):
    try:
        data = {
            "message": message,
            "reply": reply,
            "persona": persona,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table(SUPABASE_LOG_TABLE).insert(data).execute()
        print("✅ 日志已写入 Supabase")
    except Exception as e:
        print("❌ 写入 Supabase 失败:", e)
