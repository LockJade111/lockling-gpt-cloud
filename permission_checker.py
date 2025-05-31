ROLES_PERMISSIONS = {
    "军师": {
        "read": {
            "local":   ["memory", "memorys", "customers", "logs", "finance", "personas", "persona_keys", "roles"],
            "cloud":   ["memorys", "memorys_public", "customers", "logs", "finance", "personas", "persona_keys", "roles"]
        },
        "write": {
            "local": ["memory"]
        },
        "exec": {
            "local": [],
            "cloud": []
        }
    },
    "锁灵": {
        "read": {
            "cloud": ["memorys", "memorys_public"]
        },
        "write": {
            "cloud": ["memorys", "memorys_public"],
            "local": ["customers"]
        },
        "exec": {
            "cloud": [],
            "local": []
        }
    },
    "玉衡": {
        "read": {
            "local": ["memorys", "finance"]
        },
        "write": {
            "local": ["finance"]
        },
        "exec": {
            "cloud": [],
            "local": []
        }
    },
    "司铃": {
        "read": {
            "local": ["memorys", "customers", "finance"],
            "cloud": ["memorys_public"]
        },
        "write": {
            "cloud": ["memorys_public"]
            # 如有“计划表”（如 schedules）后续添加
        },
        "exec": {
            "cloud": [],
            "local": []
        }
    },
    "小徒弟": {
        "read": {
            "cloud": ["memorys_public"]
        },
        "write": {},
        "exec": {}
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

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_role_permissions(role_name):
    response = supabase.table("roles").select("permissions").eq("name", role_name).single().execute()
    return response.data["permissions"] if response.data else {}

def check_permission(role_name: str, action: str, resource: str, source: str = "local") -> bool:
    permissions = fetch_role_permissions(role_name)
    if action == "exec":
        return resource in permissions.get("exec", [])
    return resource in permissions.get(action, {}).get(source, [])




from permission_logs import log_permission_attempt

def check_permission(role_name: str, action: str, resource: str, source: str = "local") -> bool:
    permissions = fetch_role_permissions(role_name)
    result = False
    if action == "exec":
        result = resource in permissions.get("exec", [])
    else:
        result = resource in permissions.get(action, {}).get(source, [])
    log_permission_attempt(role_name, action, resource, source, "pass" if result else "deny")
    return result


# cache_permissions.py
import json
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def export_role_permissions_to_local(filepath="roles_cache.json"):
    roles = supabase.table("roles").select("name,permissions").execute().data
    cache = {r["name"]: r["permissions"] for r in roles}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print("✅ 已保存权限缓存至", filepath)

if __name__ == "__main__":
    export_role_permissions_to_local()

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
