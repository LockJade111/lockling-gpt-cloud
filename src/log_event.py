# src/log_event.py

from src.local_logger import log_to_local
from src.supabase_logger import log_to_supabase

def log_event(level, message, sensitive=False):
    """
    - sensitive=True 表示走本地数据库
    - sensitive=False 表示走 Supabase 云端
    """
    if sensitive:
        log_to_local(level, message)
    else:
        log_to_supabase(level, message)
