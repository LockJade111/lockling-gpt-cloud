# schedule_helper.py

import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def schedule_event(name, phone, address, service_desc, amount, handler):
    try:
        supabase.table("customers").insert({
            "name": name,
            "phone": phone,
            "address": address,
            "service_desc": service_desc,
            "amount": amount,
            "handled_by": handler,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        print("✅ 售后预约已成功记录")
    except Exception as e:
        print("❌ 售后预约记录失败:", e)

def log_schedule(name, service_desc, scheduled_time, handled_by):
    try:
        supabase.table("customers").insert({
            "name": name,
            "service_desc": service_desc,
            "timestamp": scheduled_time,
            "handled_by": handled_by,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        print("✅ 日程记录成功")
    except Exception as e:
        print("❌ 写入 schedule 失败:", e)
