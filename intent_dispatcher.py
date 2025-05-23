from check_permission import check_permission
from supabase_logger import write_log_to_supabase
from finance_helper import log_finance
from schedule_helper import schedule_event, log_schedule
from customer_helper import log_customer_info
from memory_helper import save_memory  # ✅ 加入上下文记忆模块

async def dispatch_intents(intent_result, message, persona):
    intent = intent_result["intent"]
    permission = intent_result.get("requires_permission", "")

    # ⛔ 权限检查
    if not check_permission(persona, permission):
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result
        }

    # ✅ 上下文记忆记录
    try:
        save_memory(persona, message, intent, context_data={})
    except Exception as e:
        print("⚠️ 记忆记录失败:", e)

    # 🎯 意图分发逻辑
    try:
        if intent == "log_finance":
            await log_finance(
                description=message,
                amount=0,  # TODO: 金额提取逻辑待接入
                category="收入",
                created_by=persona
            )
            return {"reply": "✅ 财务信息已记录", "intent": intent_result}

        elif intent == "schedule_service":
            await log_schedule(
                name="王先生",  # TODO: 可接入 GPT 提取
                service_desc="锁具售后",
                scheduled_time="2025-05-26T10:00:00",  # TODO: 动态时间解析
                handled_by="司铃"
            )
            return {"reply": "✅ 售后服务已安排，已指派给司铃", "intent": intent_result}

        elif intent == "log_customer":
            await log_customer_info(
                name="未知客户",
                phone="1234567890",
                address="未知地址",
                service_desc=message,
                amount=0,
                handled_by=persona
            )
            return {"reply": "✅ 客户信息已记录", "intent": intent_result}

        elif intent == "query_customer":
            return {"reply": "📋 客户查询功能即将上线", "intent": intent_result}

        elif intent == "grant_permission":
            return {"reply": "🔐 权限赋予功能尚未接入", "intent": intent_result}

        elif intent == "revoke_permission":
            return {"reply": "🛑 权限撤销功能尚未接入", "intent": intent_result}

        else:
            return {"reply": "🤔 无法识别的操作，请再说一遍", "intent": intent_result}

    except Exception as e:
        return {"reply": f"❌ 模块执行错误：{str(e)}", "intent": intent_result}
