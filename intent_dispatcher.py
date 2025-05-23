from check_permission import check_permission
from supabase_logger import write_log_to_supabase
from schedule_helper import schedule_event  # 如果你已实现安排模块
from finance_helper import log_finance      # 如果你已实现财务模块

def dispatch_intents(intent_list: list):
    results = []

    for intent_obj in intent_list:
        role = intent_obj.get("role")
        intent = intent_obj.get("intent")
        fields = intent_obj.get("fields", {})
        required_perm = intent_obj.get("requires_permission", "write")

        # 1. 权限判断
        if not check_permission(role, required_perm):
            results.append({
                "role": role,
                "intent": intent,
                "status": "❌ 拒绝执行",
                "reason": "权限不足"
            })
            continue

        # 2. 调度任务
        try:
            if intent == "log_entry":
                write_log_to_supabase(fields["message"], fields.get("response", ""), role)

            elif intent == "log_finance":
                log_finance(role, fields)

            elif intent == "create_schedule":
                schedule_event(role, fields)

            elif intent == "log_client":
                write_log_to_supabase(fields["message"], "客户信息记录", role)

            else:
                results.append({
                    "role": role,
                    "intent": intent,
                    "status": "⚠️ 未知意图"
                })
                continue

            results.append({
                "role": role,
                "intent": intent,
                "status": "✅ 已执行"
            })

        except Exception as e:
            results.append({
                "role": role,
                "intent": intent,
                "status": "❌ 执行失败",
                "error": str(e)
            })

    return results
