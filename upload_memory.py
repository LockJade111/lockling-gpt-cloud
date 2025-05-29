from supabase import create_client, Client
import json

# ✅ 替换成你的 Supabase 项目参数
url = "https://rjqzzauepqygriickybn.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqcXp6YXVlcHF5Z3JpaWNreWJuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5NzMxMDYsImV4cCI6MjA2MzU0OTEwNn0.EosSEpeE3NDQFgYJCDaVHe-wO4RLOL3LaMVVoiyifBE"

supabase: Client = create_client(url, key)

# ✅ 替换为你的聊天记录文件路径
with open("/Users/lockjade1/Desktop/conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

records = []
for entry in conversations:
    role = entry.get("role")
    content = entry.get("content", "").strip()
    if role and content:
        records.append({"role": role, "content": content})

if records:
    response = supabase.table("memory_logs").insert(records).execute()
    print("✅ 上传成功", response)
else:
    print("⚠️ 没有可上传的记录")
