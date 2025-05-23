# schedule_helper.py

from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_schedule(customer_name: str, datetime_str: str, handler: str, notes: str = ""):
    try:
        supabase.table("schedule").insert({
            "customer_name": customer_name,
            "appointment_time": datetime_str,
            "handled_by": handler,
            "notes": notes,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        print("❌ 写入 schedule 失败:", e)
        return False
