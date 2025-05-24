# schedule_helper.py

from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SCHEDULE_TABLE = os.getenv("SUPABASE_SCHEDULE_TABLE", "schedule")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def schedule_event(intent, persona=None):
    try:
        source = intent.get("source", "")
        timestamp = datetime.utcnow().isoformat()

        data = {
            "timestamp": timestamp,
            "event": source,
            "created_by": persona or "系统"
        }

        response = supabase.table(SCHEDULE_TABLE).insert(data).execute()
        print("✅ Schedule event logged:", response)
        return {"reply": f"✅ 已安排事项：{source}"}

    except Exception as e:
        print("❌ Failed to schedule event:", e)
        return {"reply": f"❌ 日程写入失败：{str(e)}"}
