# src/main_test.py

from src.log_event import log_event

# 测试写入
log_event("INFO", "这是普通日志记录到 Supabase", sensitive=False)
log_event("WARNING", "这是敏感日志仅写入本地", sensitive=True)
