# cache_permissions.py

import json
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def export_role_permissions_to_local(filepath="roles_cache.json"):
    try:
        roles = supabase.table("roles").select("name,permissions").execute().data
        cache = {r["name"]: r["permissions"] for r in roles}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"✅ 权限缓存成功写入：{filepath}")
    except Exception as e:
        print("❌ 导出失败：", e)

if __name__ == "__main__":
    export_role_permissions_to_local()
