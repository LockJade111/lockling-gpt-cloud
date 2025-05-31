# test_permissions.py

from permission_checker import check_permission
from src.logger_bridge import log_event

roles = ["军师", "锁灵", "玉衡", "司铃", "小徒弟"]
resources = [
    ("memory", "local"),
    ("memorys", "local"),
    ("customers", "local"),
    ("logs", "local"),
    ("finance", "local"),
    ("memorys_public", "cloud"),
    ("memorys", "cloud")
]
actions = ["read", "write", "exec"]

def test_permissions():
    print("🔍 权限校验测试开始\n")

    for role in roles:
        print(f"\n--- 角色：{role} ---")
        for action in actions:
            for resource, source in resources:
                allowed = check_permission(role, action, resource, source=source)
                status = "✅ PASS" if allowed else "❌ DENY"
                print(f"{status:8} | {role:4} | {action:5} | {resource:15} | 来源：{source}")

                # 同时记录行为日志（可选）
                log_event("test", role, action, resource, source, "pass" if allowed else "deny")

if __name__ == "__main__":
    test_permissions()
