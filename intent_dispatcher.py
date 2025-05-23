from check_permission import check_permission
from supabase_logger import write_log_to_supabase
from finance_helper import log_finance
from schedule_helper import schedule_event, log_schedule
from customer_helper import log_customer_info

async def dispatch_intents(intent_result, message, persona):
    intent = intent_result["intent"]
    permission = intent_result.get("requires_permission", "")

    # 权限检查
    if not check_permission(persona, permission):
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result
        }

    # 意图分发逻辑
    try:
        if intent == "log_finance":
            await log_finance(
                description=message,
                amount=0,  # TODO: 从 message 中提取金额
                category="收入",
                created_by=persona
            )
            return {"reply": "✅ 财务信息已记录", "intent": intent_result}

        elif intent == "schedule_service":
            await log_schedule(
                customer_name="王先生",              # TODO: 可后续 GPT 提取
                service_item="锁具售后",
                scheduled_time="2025-05-26T10:00:00",  # 可改为动态时间提取
                assigned_to="司铃",
                created_by=persona
            )
            return {"reply": "✅ 售后服务已安排，已指派给司铃", "intent": intent_result}

        elif intent == "log_customer":
            await log_customer_info(
                name="未知客户",
                phone="未知",
                address="",
                service_desc=message,
                amount=0,
                handled_by=persona
            )
            return {"reply": "✅ 客户信息已记录（基础版）", "intent": intent_result}

        elif intent == "query_customer":
            return {"reply": "📋（伪）客户查询功能待上线", "intent": intent_result}

        elif intent == "query_logs":
            return {"reply": "📜（伪）日志查询功能待接入 Supabase 查询接口", "intent": intent_result}

        elif intent == "grant_permission":
            return {"reply": "🔐（伪）权限已赋予，功能待接入角色表更新", "intent": intent_result}

        elif intent == "revoke_permission":
            return {"reply": "🛑（伪）权限已撤销，功能待接入角色表更新", "intent": intent_result}

        else:
            return {"reply": "🤔 未识别的操作，或暂未支持该指令", "intent": intent_result}

    except Exception as e:
        return {"reply": f"❌ 分发模块出错：{str(e)}", "intent": intent_result}
