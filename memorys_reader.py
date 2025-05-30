from sqlalchemy import create_engine, MetaData, Table, select, and_, or_
import os

# 环境变量
from dotenv import load_dotenv
load_dotenv()

LOCAL_DB_URL = os.getenv("LOCAL_DB_URL")
engine = create_engine(LOCAL_DB_URL, echo=False)
metadata = MetaData()
memorys = Table("memorys", metadata, autoload_with=engine)

def read_memorys(persona=None, status=None, category=None, tags=None, limit=5):
    conn = engine.connect()
    conditions = []

    if persona:
        conditions.append(memorys.c.persona == persona)
    if status:
        conditions.append(memorys.c.status == status)
    if category:
        conditions.append(memorys.c.category == category)
    if tags:
        tag_conditions = [memorys.c.tags.ilike(f"%{tag}%") for tag in tags]
        conditions.append(or_(*tag_conditions))

    query = select(memorys).order_by(memorys.c.updated_at.desc())
    if conditions:
        query = query.where(and_(*conditions))
    if limit:
        query = query.limit(limit)

    result = conn.execute(query).fetchall()
    conn.close()

    print(f"📖 读取到 {len(result)} 条 {persona or '未知角色'} 的记忆片段：\n")
    for i, row in enumerate(result, 1):
        print(f"{i}. [{row.category}] {row.content} ({row.updated_at})")
    return [dict(row._mapping) for row in result]
