import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, insert, select, delete
from sqlalchemy.exc import SQLAlchemyError

# 加载环境变量
load_dotenv()
LOCAL_DB_URL = os.getenv("LOCAL_DB_URL")

# 创建数据库引擎
engine = create_engine(LOCAL_DB_URL, echo=False)
metadata = MetaData()

def write_to_local(table_name: str, data: dict):
    """写入一条数据到本地 PostgreSQL 表"""
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        with engine.connect() as conn:
            stmt = insert(table).values(**data)
            conn.execute(stmt)
            conn.commit()
        print(f"✅ 写入成功：{table_name} → {data}")
    except SQLAlchemyError as e:
        print(f"❌ 写入失败：{e}")

def read_from_local(table_name: str, limit: int = 10):
    """读取本地表中的数据"""
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        with engine.connect() as conn:
            stmt = select(table).limit(limit)
            result = conn.execute(stmt)
            rows = result.fetchall()
            return [dict(r) for r in rows]
    except SQLAlchemyError as e:
        print(f"❌ 读取失败：{e}")
        return []

def delete_local_by_id(table_name: str, row_id: int):
    """删除本地表中指定 ID 的记录"""
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        with engine.connect() as conn:
            stmt = delete(table).where(table.c.id == row_id)
            conn.execute(stmt)
            conn.commit()
        print(f"🧹 删除成功：{table_name} ID={row_id}")
    except SQLAlchemyError as e:
        print(f"❌ 删除失败：{e}")

def write_log(role: str, intent: str, result: str, reason: str):
    """将一条操作日志写入 logs 表"""
    try:
        table = Table("logs", metadata, autoload_with=engine)
        log_data = {
            "role": role,
            "intent": intent,
            "result": result,
            "reason": reason
        }
        with engine.connect() as conn:
            stmt = insert(table).values(**log_data)
            conn.execute(stmt)
            conn.commit()
        print(f"📝 已记录日志：{intent} → {result}")
    except SQLAlchemyError as e:
        print(f"⚠️ 写日志失败：{e}")

def check_role_permission(persona, table_name):
    # 示例：玉衡只能访问 finance，军师可以访问所有
    if persona == "军师":
        return True
    if persona == "玉衡" and table_name == "finance":
        return True
    return False
