# customer_helper.py
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 确保有这个函数
def log_customer_info(name, phone, address, service_desc, amount, handled_by):
    try:
        data = {
            "name": name,
            "phone": phone,
            "address": address,
            "service_desc": service_desc,
            "amount": amount,
            "handled_by": handled_by,
            "created_at": datetime.utcnow().isoformat()
        }
        response = supabase.table("customers").insert(data).execute()
        print("✅ 客户信息已记录:", response)
    except Exception as e:
        print("❌ 客户信息记录失败:", e)
