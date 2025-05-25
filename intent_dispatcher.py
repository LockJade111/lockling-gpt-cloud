
new_name = intent.get("target", "").strip()
    secret = intent.get("secret", "").strip()

    if not new_name:
    if not persona or not new_name or not secret:
        return {
            "status": "fail",
            "reply": "❌ 注册失败：未指定新 persona 名称。",
            "reply": "❗ 缺少 persona、target 或 secret 字段。",
            "intent": intent
        }

    if not check_persona_secret(persona, secret):
        return {
            "status": "fail",
            "reply": "❌ 注册失败：操作者密钥错误。",
            "intent": intent
        }

    try:
        result = register_persona(new_name, secret)
        write_log_to_supabase(persona, intent, "success", f"注册新 persona：{new_name}")
        return {
            "status": "success",
            "reply": f"✅ 已注册新角色：{new_name}",
            "intent": intent
        }
    except Exception as e:
        write_log_to_supabase(persona, intent, "fail", str(e))
        return {
            "status": "fail",
            "reply": f"❌ 注册失败：{str(e)}",
            "intent": intent
        }
    result = register_persona(persona, new_name, secret)
    return {
        "status": "success" if result else "fail",
        "reply": "✅ 注册成功" if result else "⚠️ 注册失败",
        "intent": intent
    }

# ✅ 授权权限 intent
def handle_authorize(intent):
    print("📥 收到意图：authorize")
# ✅ 删除 persona
def handle_delete_persona(intent):
    print("📥 收到意图：delete_persona")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()
    permission = intent.get("permission", "").strip()

    if not target or not permission:
        return {
            "status": "fail",
            "reply": "❌ 授权失败：缺少目标或权限类型。",
            "intent": intent
    result = delete_persona(persona, target)
    return {
        "status": "success" if result else "fail",
        "reply": "✅ 删除成功" if result else "⚠️ 删除失败",
        "intent": intent
    }

# ✅ 分发器类
class Dispatcher:
    def __init__(self):
        self.handlers = {
            "confirm_secret": handle_confirm_secret,
            "register_persona": handle_register_persona,
            "delete_persona": handle_delete_persona,
            # 可拓展更多意图
        }

    try:
        res = supabase.table("roles").select("permissions").eq("role", target).execute()
        if not res.data:
            write_log_to_supabase(persona, intent, "fail", f"目标 {target} 不存在")
            return {
                "status": "fail",
                "reply": f"❌ 授权失败：目标角色 {target} 不存在。",
                "intent": intent
            }
    async def dispatch(self, intent):
        intent_type = intent.get("intent_type")
        handler = self.handlers.get(intent_type)

        current = res.data[0].get("permissions", [])
        if permission in current:
            write_log_to_supabase(persona, intent, "info", f"{target} 已有 {permission}")
            return {
                "status": "info",
                "reply": f"⚠️ {target} 已拥有 {permission} 权限。",
                "intent": intent
            }

        updated = current + [permission]
        supabase.table("roles").update({"permissions": updated}).eq("role", target).execute()
        write_log_to_supabase(persona, intent, "success", f"授权 {target} -> {permission}")
        return {
            "status": "success",
            "reply": f"✅ 已授权 {target} 拥有 {permission} 权限。",
            "intent": intent
        }

    except Exception as e:
        write_log_to_supabase(persona, intent, "fail", str(e))
        return {
            "status": "fail",
            "reply": f"❌ 授权失败：{str(e)}",
            "intent": intent
        }

# ✅ 撤销权限 intent
def handle_revoke(intent):
    print("📥 收到意图：revoke")
    persona = intent.get("persona", "").strip()
    target = intent.get("target", "").strip()
    permission = intent.get("permission", "").strip()

    if not target or not permission:
        return {
            "status": "fail",
            "reply": "❌ 撤销失败：缺少目标或权限类型。",
            "intent": intent
        }

    try:
        res = supabase.table("roles").select("permissions").eq("role", target).execute()
        if not res.data:
            write_log_to_supabase(persona, intent, "fail", f"目标 {target} 不存在")
        if handler:
            return handler(intent)
        else:
            return {
                "status": "fail",
                "reply": f"❌ 撤销失败：目标角色 {target} 不存在。",
                "intent": intent
            }

        current = res.data[0].get("permissions", [])
        if permission not in current:
            write_log_to_supabase(persona, intent, "info", f"{target} 原本不具备 {permission}")
            return {
                "status": "info",
                "reply": f"⚠️ {target} 原本就不具备 {permission} 权限。",
                "reply": f"❓ 未知意图类型：{intent_type}",
                "intent": intent
            }

        updated = [p for p in current if p != permission]
        supabase.table("roles").update({"permissions": updated}).eq("role", target).execute()
        write_log_to_supabase(persona, intent, "success", f"撤销 {target} -> {permission}")
        return {
            "status": "success",
            "reply": f"✅ 已撤销 {target} 的 {permission} 权限。",
            "intent": intent
        }

    except Exception as e:
        write_log_to_supabase(persona, intent, "fail", str(e))
        return {
            "status": "fail",
            "reply": f"❌ 撤销失败：{str(e)}",
            "intent": intent
        }

# ✅ 主调度器
def dispatch(intent: dict):
    intent_type = intent.get("intent_type", "")
    if intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "register_persona":
        return handle_register_persona(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "revoke":
        return handle_revoke(intent)
    else:
        return {
            "status": "info",
            "reply": f"🤖 尚未支持的意图类型：{intent_type}",
            "intent": intent
        }
# ✅ 导出 dispatcher 实例供主程序使用
dispatcher = Dispatcher()
