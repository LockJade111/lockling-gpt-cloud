# dal.py
from local_db import read_from_local as query_local_db, write_to_local as write_local_db
from cloud_db import query_cloud_db, write_cloud_db
from permission_checker import check_permission

class DataAccessLayer:
    def __init__(self, role):
        self.role = role

    def read(self, resource, query_params):
        if not check_permission(self.role, "read", resource):
            raise PermissionError(f"角色 {self.role} 无权读取资源 {resource}")

        if self.role == "军师":
            result = query_local_db(resource, query_params)
            if not result:
                result = query_cloud_db(resource, query_params)
        elif self.role == "锁灵":
            result = query_cloud_db(resource, query_params)
            if not result:
                result = query_local_db(resource, query_params)
        else:
            result = query_cloud_db(resource, query_params)
        return result

    def write(self, resource, data):
        if not check_permission(self.role, "write", resource):
            raise PermissionError(f"角色 {self.role} 无权写入资源 {resource}")

        if self.role == "军师":
            write_local_db(resource, data)
            write_cloud_db(resource, data)  # 可改成异步执行
        elif self.role == "锁灵":
            write_cloud_db(resource, data)
        else:
            raise PermissionError(f"角色 {self.role} 不允许写操作")

# 简单同步示范（可扩展为异步线程或任务队列）
def sync_local_to_cloud(resource, data):
    try:
        write_cloud_db(resource, data)
        print(f"同步成功：{resource}")
    except Exception as e:
        print(f"同步失败：{e}")

if __name__ == "__main__":
    dal = DataAccessLayer("军师")

    # 读测试
    try:
        recs = dal.read("memorys", {"persona": "军师"})
        print("读取记录:", recs)
    except PermissionError as e:
        print(e)

    # 写测试
    try:
        dal.write("memorys", {"persona": "军师", "content": "测试写入", "tags": '{"测试"}'})
        print("写入成功")
    except PermissionError as e:
        print(e)
