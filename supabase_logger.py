import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "logs")  # 默认写入 logs 表

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_log_to_supabase(message, persona, intent_result, reply):
    try:
        data = {
            "message": message,
            "persona": persona,
            "intent_result": json.dumps(intent_result, ensure_ascii=False),  # 存为 JSON 字符串
            "reply": reply
        }
        response = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志已写入 Supabase")
        return response
    except Exception as e:
        print(f"❌ 写入 Supabase 失败: {e}")
        return None
