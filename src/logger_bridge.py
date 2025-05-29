import os
from src import supabase_logger, local_logger

# ✅ 默认使用 Supabase除非设置为 local
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

def write_log(message, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    if USE_LOCAL_DB:
        local_logger.write_log_to_local(message, reply, intent_result, status, source, raw_intent)
    else:
        supabase_logger.write_log_to_supabase(message, reply, intent_result, status, source, raw_intent)
