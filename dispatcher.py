from cloud_db import write_to_cloud
from local_db import write_to_local, write_log
from memorys_reader import read_memorys

from dal import DataAccessLayer

def process_command(role, resource, action, data=None, query_params=None):
    dal = DataAccessLayer(role)
    try:
        if action == "read":
            return dal.read(resource, query_params or {})
        elif action == "write":
            return dal.write(resource, data)
        else:
            raise ValueError("不支持的操作类型")
    except PermissionError as e:
        print(f"权限拒绝: {e}")
        # 这里可以写日志或返回错误给调用方
        return None

if __name__ == "__main__":
    # 示例：军师写入一条记忆
    process_command("军师", "memorys", "write", data={
        "persona": "军师",
        "content": "新的系统更新",
        "tags": '{"系统","更新"}',
        "category": "系统通告",
        "trust_level": 5,
        "source": "dispatcher"
    })

    # 示例：锁灵尝试读取公共记忆
    records = process_command("锁灵", "memorys_public", "read", query_params={"persona": "锁灵"})
    print(records)


def store_memory(persona, content, category="默认", trust_level=3, source="dispatcher", tags="", status="active"):
    # 转成PG数组格式字符串
    if tags and isinstance(tags, str):
        tags_array = '{' + ','.join([f'"{tag.strip()}"' for tag in tags.split(',')]) + '}'
    else:
        tags_array = tags

    data = {
        "persona": persona,
        "content": content,
        "trust_level": trust_level,
        "category": category,
        "source": source,
        "status": status,
        "tags": tags_array,
    }

    try:
        # 写入本地
        write_to_local("memorys", data)
        write_log("dispatcher", "写入本地 memorys", "成功", str(data))
    except Exception as e:
        write_log("dispatcher", "写入本地 memorys", "失败", str(e))

    try:
        # 写入云端
        write_to_cloud("memorys", data)
        write_log("dispatcher", "写入云端 memorys", "成功", str(data))
    except Exception as e:
        write_log("dispatcher", "写入云端 memorys", "失败", str(e))
        print(f"⚠️ 操作失败：{e}")
        raise

def retrieve_memory(persona, category=None, status="active", tags=None, limit=5):
    try:
        records = read_memorys(
            persona=persona,
            category=category,
            status=status,
            tags=tags,
            limit=limit
        )
        return records
    except Exception as e:
        write_log("dispatcher", "操作失败", "异常捕获", str(e))
        print(f"⚠️ 查询失败：{e}")
        return []

# 🧪 测试入口
if __name__ == "__main__":
    try:
        print("📥 写入测试：")
        store_memory(
            persona="军师",
            content="Lockling 启动成功",
            category="系统通告",
            trust_level=4,
            tags="启动,成功"
        )

        print("\n📤 查询测试：")
        results = retrieve_memory(persona="军师", category="系统通告", tags=["成功"])
        for idx, item in enumerate(results, 1):
            print(f"{idx}. [{item['category']}] {item['content']} ({item['updated_at']})")

        print("\n🔎 测试读取 Lockling 的全部记忆：")
        read_memorys(persona="Lockling", limit=5)

        print("\n🔎 测试读取 军师 的 active 系统测试类记忆：")
        read_memorys(persona="军师", category="系统测试", status="active")

        print("\n🔎 测试读取 军师 的全部最新记忆：")
        read_memorys("军师", limit=5)

    except Exception as e:
        write_log("dispatcher", "失败", str(e))
        print(f"⚠️ 主程序异常：{e}")
