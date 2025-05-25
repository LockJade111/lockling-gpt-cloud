✅ 注册 persona（支持写入角色）
# ✅ 注册 persona（支持写入角色，返回布尔值 + 消息）
def register_persona(persona: str, secret: str, created_by="系统", role="user"):
    # 查重
    existing = supabase.table(TABLE).select("persona").eq("persona", persona).execute()
    if existing.data:
        return False, f"角色 {persona} 已存在"

    hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
    result = supabase.table(TABLE).insert({
        "persona": persona,
        "secret_hash": hashed,
        "created_by": created_by,
        "role": role,
        "active": True,
        "failed_attempts": 0,
        "locked": False
    }).execute()
    return result

    try:
        result = supabase.table(TABLE).insert({
            "persona": persona,
            "secret_hash": hashed,
            "created_by": created_by,
            "role": role,
            "active": True,
            "failed_attempts": 0,
            "locked": False
        }).execute()
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"

# ✅ 验证 persona 密钥（含失败计数与锁定机制）
def check_persona_secret(persona: str, input_secret: str) -> bool:
@@ -44,49 +53,14 @@ def check_persona_secret(persona: str, input_secret: str) -> bool:
            }).eq("persona", persona).execute()
            return True
        else:
            new_fail_count = row.get("failed_attempts", 0) + 1
            update_data = {
                "failed_attempts": new_fail_count
            }
            if new_fail_count >= 5:
            new_count = row.get("failed_attempts", 0) + 1
            update_data = {"failed_attempts": new_count}
            if new_count >= 5:
                update_data["locked"] = True
                print(f"[⚠️] 密钥失败超过 5 次，已锁定 persona：{persona}")

            supabase.table(TABLE).update(update_data).eq("persona", persona).execute()
            return False
    except Exception as e:
        print(f"[❌] 密钥验证异常：{e}")
        print(f"[异常] 密钥验证异常: {e}")
        return False

# ✅ 撤销授权权限（active = False）
def revoke_persona(persona: str):
    return supabase.table(TABLE).update({
        "active": False
    }).eq("persona", persona).execute()

# ✅ 删除 persona（直接从表中移除）
def delete_persona(persona: str):
    return supabase.table(TABLE).delete().eq("persona", persona).execute()

# ✅ 解锁 persona（将军专属）
def unlock_persona(persona: str) -> bool:
    try:
        result = supabase.table(TABLE).update({
            "locked": False,
            "failed_attempts": 0
        }).eq("persona", persona).execute()
        return True if result.data else False
    except Exception as e:
        print(f"[❌] 解锁失败: {e}")
        return False

# ✅ 查询 persona 权限等级
def get_persona_role(persona: str) -> str:
    try:
        result = supabase.table(TABLE).select("role").eq("persona", persona).limit(1).execute()
        if result.data:
            return result.data[0].get("role", "user")
        else:
            return "user"
    except Exception:
        return "user"
# ✅ 可扩展：注销、删除等接口可后续添加
