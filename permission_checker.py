# permission_checker.py

ROLES_PERMISSIONS = {
    "军师": {
        "read": {
            "local": ["memorys", "logs", "finance", "customers"],
            "cloud": ["memorys_public", "customers_public"]
        },
        "write": {
            "local": ["memorys", "logs", "finance", "customers"],
            "cloud": ["memorys_public"]
        },
        "exec": ["授权", "调度", "管理"]
    },
    "锁灵": {
        "read": {
            "local": [],
            "cloud": ["memorys", "memorys_public", "customers_public"]
        },
        "write": {
            "local": [],
            "cloud": ["memorys", "memorys_public"]
        },
        "exec": []
    },
    "玉衡": {
        "read": {
            "local": ["memorys", "finance"],
            "cloud": []
        },
        "write": {
            "local": ["memorys"],
            "cloud": []
        },
        "exec": []
    },
    "司铃": {
        "read": {
            "local": ["memorys", "finance", "customers"],
            "cloud": ["memorys_public"]
        },
        "write": {
            "local": [],
            "cloud": ["memorys_public", "customers_public"]
        },
        "exec": []
    },
    "小徒弟": {
        "read": {
            "local": [],
            "cloud": ["memorys_public"]
        },
        "write": {
            "local": [],
            "cloud": []
        },
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

# ✅ 权限判断（支持 local/cloud + exec）
def has_permission(persona_id: str, action: str, resource: str, source: str = "local") -> bool:
    persona = PERSONA_REGISTRY.get(persona_id)
    if not persona:
        return False
    permissions = persona.get("permissions", {})
    if action == "exec":
        return resource in permissions.get("exec", [])
    return resource in permissions.get(action, {}).get(source, [])

# ✅ 支持中文角色名 → persona 映射
def check_permission(role_name: str, action: str, resource: str, source: str = "local") -> bool:
    role_to_persona = {
        "军师": "persona_1",
        "锁灵": "persona_2",
        "玉衡": "persona_3",
        "司铃": "persona_4",
        "小徒弟": "persona_5",
    }
    persona_id = role_to_persona.get(role_name)
    if not persona_id:
        return False
    return has_permission(persona_id, action, resource, source)

# ✅ 测试用例（包含本地 + 云端）
if __name__ == "__main__":
    test_cases = [
        ("军师", "read", "memorys", "local"),
        ("军师", "read", "memorys_public", "cloud"),
        ("锁灵", "write", "memorys_public", "cloud"),
        ("玉衡", "read", "finance", "local"),
        ("司铃", "write", "customers_public", "cloud"),
        ("小徒弟", "read", "memorys_public", "cloud"),
        ("小徒弟", "read", "finance", "local"),
        ("军师", "exec", "调度", ""),  # exec 没有 source
    ]

    for role, action, resource, source in test_cases:
        if action == "exec":
            allowed = check_permission(role, action, resource)
        else:
            allowed = check_permission(role, action, resource, source)
        print(f"角色 {role} 是否可 {action} {resource}（{source}）：{allowed}")
