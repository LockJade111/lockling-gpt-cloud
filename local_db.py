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

def read_from_local(table_name: str, query_params: dict = None):
    """读取本地表中的数据，支持字段筛选 + limit 控制"""
    try:
        query_params = query_params or {}
        table = Table(table_name, metadata, autoload_with=engine)

        # 处理 LIMIT 参数
        limit = query_params.pop("limit", 10)

        # 构建 SELECT 语句
        stmt = select(table)

        # 构建 WHERE 条件（基于 query_params 剩余字段）
        for key, value in query_params.items():
            if hasattr(table.c, key):
                stmt = stmt.where(getattr(table.c, key) == value)

        # 添加 LIMIT
        stmt = stmt.limit(limit)

        # 执行查询，转换为字典结构返回
        with engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
            return [dict(r) for r in result]

    except SQLAlchemyError as e:
        print(f"❌ 本地读取失败：{e}")
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
