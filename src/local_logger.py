# src/local_logger.py
import sqlite3
from datetime import datetime
import os
def write_log_to_local(message, result, intent, status):    
    conn = sqlite3.connect("lockling_logs.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT,
            source TEXT,
            content TEXT
        )
    ''')

    timestamp = datetime.datetime.now().isoformat()
    event_type = intent.get("intent_type", "unknown")
    source = intent.get("persona", "unknown")

    cursor.execute('''
        INSERT INTO logs (timestamp, event_type, source, content)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, event_type, source, f"{message} => {result}"))

    conn.commit()
    conn.close()

    print("✅ 已写入本地日志 lockling_logs.db")

# 定义数据库文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lockling_logs.db")

# 创建或连接数据库
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# 初始化日志表
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT,
            source TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 写入日志
def log_event(event_type, source, content):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO logs (timestamp, event_type, source, content)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, event_type, source, content))
    conn.commit()
    conn.close()

# 启动时初始化表
if __name__ == "__main__":
    init_db()
    log_event("test", "local_logger", "本地日志系统测试写入成功")
    print("日志已写入 lockling_logs.db")
