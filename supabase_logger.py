import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 加载 .env（适用于本地调试）
load_dotenv()

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "logs")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 主函数：写入日志记录
def write_log_to_supabase(message: str, persona: str, intent_result: dict, reply: str):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",  # UTC时间戳
            "persona": persona,
            "message": message,  # 用户输入
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False),
            "reason": intent_result.get("reason", ""),
            "reply": reply,
            "source": intent_result.get("source", ""),  # 原始文本
            "env": os.getenv("NODE_ENV", "local"),  # 环境标记
            "raw_intent": json.dumps(intent_result, ensure_ascii=False)
        }

        response = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志已写入 Supabase ✅")
        return response

    except Exception as e:
        print(f"❌ 写入 Supabase 失败: {e}")
        return None
