from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FINANCE_TABLE = os.getenv("SUPABASE_FINANCE_TABLE", "finance")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def insert_finance_log(description: str, amount: float, category: str, created_by: str):
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "description": description,
        "amount": amount,
        "category": category,
        "created_by": created_by,
    }

    try:
        res = supabase.table(FINANCE_TABLE).insert(data).execute()
        print("✅ 财务记录已写入 Supabase")
    except Exception as e:
        print("❌ 写入财务记录失败:", e)
