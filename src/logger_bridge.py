import os
from src import supabase_logger, local_logger

# ✅ 默认使用 Supabase，除非设置环境变量 USE_LOCAL_DB=true
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

# 📘 原写法：用于对话系统或 intent-based 日志
def write_log(message, reply, intent_result=None, status="success", source="cloud", raw_intent=None):
    if USE_LOCAL_DB:
        local_logger.write_log_to_local(message, reply, intent_result, status, source, raw_intent)
    else:
        supabase_logger.write_log_to_supabase(message, reply, intent_result, status, source, raw_intent)

# ✅ 新增：通用权限/行为日志系统（用于 dal.py、权限判断等）
def log_event(event_type, actor, action, resource, source, status, message=None):
    """
    通用日志记录接口，用于数据访问、权限判断、系统行为等。
    """
    log_data = {
        "message": f"[{event_type.upper()}] {actor} → {action} {resource}",
        "reply": message or "",
        "intent_result": f"{action}_{resource}",
        "status": status,
        "source": source,
        "raw_intent": f"{actor}:{action}:{resource}"
    }
    write_log(**log_data)


# ✅ 新增：通用权限/行为日志系统（用于 dal.py、权限判断等）
def log_event(event_type, actor, action, resource, source, status, message=None):
    """
    通用日志记录接口，用于数据访问、权限判断、系统行为等。
    """
    log_data = {
        "message": f"[{event_type.upper()}] {actor} → {action} {resource}",
        "reply": message or "",
        "intent_result": f"{action}_{resource}",
        "status": status,
        "source": source,
        "raw_intent": f"{actor}:{action}:{resource}"
    }
    write_log(**log_data)
