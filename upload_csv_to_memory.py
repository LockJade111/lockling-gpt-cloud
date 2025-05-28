import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 加载环境变量
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ✅ CSV 文件路径（改为你桌面上的路径）
csv_path = "/Users/lockjade1/Desktop/memory.csv"

# ✅ 加载 CSV 并清洗数据
df = pd.read_csv(csv_path)

# ✅ 替换非法 float 值，填空防止 JSON 报错
df = df.replace([np.inf, -np.inf], np.nan)
df = df.fillna("")

# ✅ 上传到 Supabase
for _, row in df.iterrows():
    data = {
        "role": str(row.get("role", "")),
        "content": str(row.get("content", "")),
        "tag": str(row.get("tag", "导入自CSV")),
        "sensitive": bool(row.get("sensitive", False)),
    }
    try:
        response = supabase.table("memory").insert(data).execute()
        print("✅ 上传成功:", response)
    except Exception as e:
        print("❌ 上传失败:", e)
