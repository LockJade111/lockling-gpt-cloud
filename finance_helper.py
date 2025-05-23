from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FINANCE_TABLE = os.getenv("SUPABASE_FINANCE_TABLE", "finance")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def log_finance(description, amount, category, created_by):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "amount": amount,
            "category": category,
            "created_by": created_by
        }
        response = supabase.table(FINANCE_TABLE).insert(data).execute()
        print("✅ Finance log created:", response)
    except Exception as e:
        print("❌ Failed to write finance log:", e)
