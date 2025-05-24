import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ 加载 .env 环境变量（仅限本地调试时使用）
load_dotenv()

# ✅ 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "logs")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 核心写入函数
def write_log_to_supabase(message: str, persona: str, intent_result: dict, reply: str):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",  # 精确时间戳
            "persona": persona,
            "message": message,
            "intent_type": intent_result.get("intent_type", "unknown"),
            "target": intent_result.get("target", ""),
            "allow": intent_result.get("allow", False),
            "reason": intent_result.get("reason", ""),
            "reply": reply,
            "raw_intent": json.dumps(intent_result, ensure_ascii=False)  # 完整 intent 结构
        }

        response = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print("✅ 日志已写入 Supabase ✅")
        return response

    except Exception as e:
        print(f"❌ 写入 Supabase 失败: {e}")
        return None
