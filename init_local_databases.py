import sqlite3
from datetime import datetime

def init_lockling_memory():
    conn = sqlite3.connect("lockling_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona TEXT,
        content TEXT,
        trust_level INTEGER,
        category TEXT,
        tags TEXT,
        updated_at TEXT,
        source TEXT,
        is_strategic BOOLEAN DEFAULT 1,
        version INTEGER DEFAULT 1
    );
    """)
    conn.commit()
    conn.close()
    print("✅ 已创建 lockling_memory.db")

def init_finance():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item TEXT,
        amount REAL,
        category TEXT,
        client_id INTEGER,
        method TEXT,
        status TEXT,
        created_by TEXT,
        memo TEXT,
        project_code TEXT
    );
    """)
    conn.commit()
    conn.close()
    print("✅ 已创建 finance.db")

def init_schedule():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        customer_id INTEGER,
        task TEXT,
        location TEXT,
        status TEXT,
        assigned_to TEXT,
        project_code TEXT,
        priority_level INTEGER DEFAULT 1
    );
    """)
    conn.commit()
    conn.close()
    print("✅ 已创建 schedule.db")

def init_customers():
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        tag TEXT,
        created_at TEXT,
        note TEXT,
        visit_count INTEGER DEFAULT 0,
        last_visit TEXT,
        customer_type TEXT,
        loyalty_score INTEGER DEFAULT 0,
        risk_flag BOOLEAN DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()
    print("✅ 已创建 customers.db")

if __name__ == "__main__":
    init_lockling_memory()
    init_finance()
    init_schedule()
    init_customers()
    print("🎯 所有本地数据库已初始化完成！")
