# dal.py

from local_db import read_from_local as query_local_db, write_to_local as write_local_db
from cloud_db import query_cloud_db, write_to_cloud
from permission_checker import check_permission
from src.logger_bridge import log_event

class DataAccessLayer:
    def __init__(self, role):
        self.role = role

    def read(self, resource, query_params=None):
        query_params = query_params or {}
        result = None

        # ① 本地读取
        if check_permission(self.role, "read", resource, source="local"):
            try:
                result = query_local_db(resource, query_params)
                if result:
                    log_event("access", self.role, "read", resource, "local", "success", "本地读取成功")
                    print(f"[LOCAL] 读取成功：{resource}")
                    return result
                else:
                    log_event("access", self.role, "read", resource, "local", "empty", "本地无结果")
            except Exception as e:
                log_event("access", self.role, "read", resource, "local", "error", str(e))
                raise e
        else:
            log_event("auth", self.role, "read", resource, "local", "denied", "无本地读取权限")

        # ② 云端读取
        if check_permission(self.role, "read", resource, source="cloud"):
            try:
                result = query_cloud_db(resource, query_params)
                if result:
                    log_event("access", self.role, "read", resource, "cloud", "success", "云端读取成功")
                    print(f"[CLOUD] 读取成功：{resource}")
                    return result
                else:
                    log_event("access", self.role, "read", resource, "cloud", "empty", "云端无结果")
            except Exception as e:
                log_event("access", self.role, "read", resource, "cloud", "error", str(e))
                raise e
        else:
            log_event("auth", self.role, "read", resource, "cloud", "denied", "无云端读取权限")

        # 若无结果返回
        raise PermissionError(f"❌ 角色 {self.role} 无权限或无数据可读 → {resource}")

    def write(self, resource, data):
        wrote = False

        # ① 本地写入
        if check_permission(self.role, "write", resource, source="local"):
            try:
                write_local_db(resource, data)
                log_event("access", self.role, "write", resource, "local", "success", "本地写入成功")
                print(f"[LOCAL] 写入成功：{resource}")
                wrote = True
            except Exception as e:
                log_event("access", self.role, "write", resource, "local", "error", str(e))
                raise e
        else:
            log_event("auth", self.role, "write", resource, "local", "denied", "无本地写入权限")

        # ② 云端写入
        if check_permission(self.role, "write", resource, source="cloud"):
            try:
                write_to_cloud(resource, data)
                log_event("access", self.role, "write", resource, "cloud", "success", "云端写入成功")
                print(f"[CLOUD] 写入成功：{resource}")
                wrote = True
            except Exception as e:
                log_event("access", self.role, "write", resource, "cloud", "error", str(e))
                raise e
        else:
            log_event("auth", self.role, "write", resource, "cloud", "denied", "无云端写入权限")

        if not wrote:
            raise PermissionError(f"❌ 角色 {self.role} 无权限写入 → {resource}")

        return True

# 🧪 示例测试代码（可保留用于终端快速验证）
if __name__ == "__main__":
    dal = DataAccessLayer("军师")

    try:
        data = dal.read("memorys", {"persona": "军师"})
        print("读取结果:", data)
    except PermissionError as e:
        print(e)

    try:
        dal.write("memorys", {"persona": "军师", "content": "测试数据", "tags": ["测试"]})
    except PermissionError as e:
        print(e)
