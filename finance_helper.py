# finance_helper.py

from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FINANCE_TABLE = os.getenv("SUPABASE_FINANCE_TABLE", "finance")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_finance(intent, persona=None):
    try:
        source = intent.get("source", "")
        timestamp = datetime.utcnow().isoformat()
        amount = 0
        description = source

        # ⛏️ 简易金额提取（可后续 NLP 精细处理）
        import re
        match = re.search(r'(\d+)[元刀块]', source)
        if match:
            amount = float(match.group(1))

        data = {
            "timestamp": timestamp,
            "description": description,
            "amount": amount,
            "category": "income",
            "created_by": persona or "系统"
        }

        response = supabase.table(FINANCE_TABLE).insert(data).execute()
        print("✅ Finance log created:", response)
        return {"reply": f"✅ 已记录 {description}（金额约 {amount}）"}

    except Exception as e:
        print("❌ Failed to write finance log:", e)
        return {"reply": f"❌ 写入失败{str(e)}"}
