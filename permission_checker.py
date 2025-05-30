# permission_checker.py

ROLES_PERMISSIONS = {
    "军师": {
        "read": ["memory", "memorys", "logs", "finance"],
        "write": ["memory", "memorys", "logs", "finance"],
        "exec": ["授权", "调度", "管理"]
    },
    "锁灵": {
        "read": ["memorys", "memorys_public"],
        "write": ["memorys", "memorys_public"],
        "exec": []
    },
    "玉衡": {
        "read": ["memorys", "finance"],
        "write": ["memorys"],
        "exec": []
    },
    "司铃": {
        "read": ["memorys", "memorys_public"],
        "write": ["memorys_public"],
        "exec": []
    },
    "小徒弟": {
        "read": ["memorys_public"],
        "write": [],
        "exec": []
    }
}

PERSONA_REGISTRY = {
    "persona_1": {"name": "军师", "permissions": ROLES_PERMISSIONS.get("军师", {})},
    "persona_2": {"name": "锁灵", "permissions": ROLES_PERMISSIONS.get("锁灵", {})},
    "persona_3": {"name": "玉衡", "permissions": ROLES_PERMISSIONS.get("玉衡", {})},
    "persona_4": {"name": "司铃", "permissions": ROLES_PERMISSIONS.get("司铃", {})},
    "persona_5": {"name": "小徒弟", "permissions": ROLES_PERMISSIONS.get("小徒弟", {})},
}

        
def has_permission(persona_id: str, action: str, resource: str) -> bool:
    """
    根据 persona_id 查注册表，判断是否有权限执行 action 于 resource
    """
    persona = PERSONA_REGISTRY.get(persona_id)
    if not persona:
        return False
    permissions = persona.get("permissions", {})
    allowed_resources = permissions.get(action, [])
    return resource in allowed_resources
    


# 测试用例示范
if __name__ == "__main__":
    test_cases = [
        ("persona_1", "read", "memory"),
        ("persona_2", "write", "memorys_public"),
        ("persona_3", "read", "finance"),
        ("persona_4", "write", "memorys_public"),
        ("persona_5", "write", "memorys_public"),
    ]
    for pid, act, res in test_cases:
        perm = PERSONA_REGISTRY.get(pid, {}).get("permissions", {})
        allowed = res in perm.get(act, [])
        print(f"角色 {pid} 是否可{act} {res}：{allowed}")


