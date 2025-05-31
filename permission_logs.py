# permission_logs.py

import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "permission_access.log")

# 确保日志文件目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def log_permission_attempt(role, action, target, source, result, reason=""):
    """
    记录一次权限操作尝试
    """
    timestamp = datetime.now().isoformat()
    entry = (
        f"{timestamp} | {result.upper():<5} | {role:<6} | {action:<6} | {target:<15} "
        f"| 来源：{source:<6} | {reason}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

# 示例测试调用
if __name__ == "__main__":
    log_permission_attempt("锁灵", "read", "memorys", "cloud", "pass")
    log_permission_attempt("小徒弟", "write", "customers", "local", "deny", "无写入权限")
