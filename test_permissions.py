# test_permissions.py

from dal import DataAccessLayer  # 你的统一数据访问层

def run_permission_tests():
    roles = ["军师", "锁灵", "玉衡", "司铃", "小徒弟"]
    resources = ["memorys", "memorys_public", "finance", "logs"]
    actions = ["read", "write", "exec"]

    for role in roles:
        dal = DataAccessLayer(role)
        for resource in resources:
            for action in actions:
                try:
                    if action == "read":
                        dal.read(resource, {})
                        print(f"[PASS] {role} 可读 {resource}")
                    elif action == "write":
                        dal.write(resource, {"test": "data"})
                        print(f"[PASS] {role} 可写 {resource}")
                    else:
                        # exec 权限测试根据具体实现写
                        print(f"[INFO] {role} 执行 {resource} 权限测试需定制")
                except PermissionError:
                    print(f"[DENY] {role} 无权 {action} {resource}")
                except Exception as e:
                    print(f"[ERROR] {role} {action} {resource} 时发生错误: {e}")

if __name__ == "__main__":
    run_permission_tests()
