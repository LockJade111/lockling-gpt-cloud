import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def write_to_cloud(table_name: str, data: dict):
    try:
        res = supabase.table(table_name).insert(data).execute()
        print(f"☁️ 已写入 Supabase 云端：{table_name} → {data}")
        return res
    except Exception as e:
        print(f"❌ 云端写入失败：{e}")
        return None

def query_cloud_db(table_name: str, filters: dict = None, limit: int = 10):
    try:
        query = supabase.table(table_name).select("*")
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        res = query.limit(limit).execute()
        if res.data:
            print(f"🔎 查询云端表 {table_name} 条数: {len(res.data)}")
            return res.data
        else:
            print(f"🔎 查询云端表 {table_name} 无匹配数据")
            return []
    except Exception as e:
        print(f"❌ 云端查询失败：{e}")
        return None
