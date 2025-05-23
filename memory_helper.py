from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MEMORY_TABLE = os.getenv("SUPABASE_MEMORY_TABLE", "memory")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def write_memory(persona, message, reply):
    try:
        supabase.table(MEMORY_TABLE).insert({
            "persona": persona,
            "message": message,
            "reply": reply,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        print("✅ 记忆写入成功")
    except Exception as e:
        print("❌ 记忆写入失败:", e)
