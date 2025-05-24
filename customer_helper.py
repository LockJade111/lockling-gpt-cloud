# customer_helper.py

from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CUSTOMER_TABLE = os.getenv("SUPABASE_CUSTOMER_TABLE", "customers")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_customer(intent, persona=None):
    try:
        source = intent.get("source", "")
        timestamp = datetime.utcnow().isoformat()

        data = {
            "timestamp": timestamp,
            "note": source,
            "logged_by": persona or "系统"
        }

        response = supabase.table(CUSTOMER_TABLE).insert(data).execute()
        print("✅ Customer log created:", response)
        return {"reply": f"✅ 已记录客户内容：{source}"}

    except Exception as e:
        print("❌ Failed to log customer data:", e)
        return {"reply": f"❌ 写入失败：{str(e)}"}
