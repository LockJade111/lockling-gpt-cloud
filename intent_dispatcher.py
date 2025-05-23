from check_permission import check_permission
from supabase_logger import write_log_to_supabase
from finance_helper import log_finance
from schedule_helper import schedule_event

async def dispatch_intents(intent_result, message, persona):
    intent = intent_result["intent"]
    permission = intent_result.get("requires_permission", "")

    # 权限判断
    if not check_permission(persona, permission):
        return {
            "reply": f"⚠️ {persona} 没有权限执行该操作。",
            "intent": intent_result
        }

    # 分发逻辑
    try:
        if intent == "log_finance":
            await log_finance(
                description=message,
                amount=0,  # 可接入 GPT 提取金额的下一阶段功能
                category="收入",
                created_by=persona
            )
            return {"reply": "✅ 财务信息已记录", "intent": intent_result}

        elif intent == "schedule_service":
            await schedule_event(
                what="售后服务",  # 可改为GPT提取
                when="稍后",      # 可接入具体时间
                by=persona
            )
            return {"reply": "✅ 售后已安排，司铃将跟进", "intent": intent_result}

        elif intent == "query_logs":
            return {"reply": "📜 （伪）日志查询功能待接入 Supabase 查询接口", "intent": intent_result}

        elif intent == "grant_permission":
            return {"reply": "✅ （伪）权限已变更，功能待接入数据库写入", "intent": intent_result}

        elif intent == "revoke_permission":
            return {"reply": "✅ （伪）权限已移除，功能待接入数据库写入", "intent": intent_result}

        else:
            return {"reply": "🤔 未识别的操作，或暂未支持", "intent": intent_result}

    except Exception as e:
        return {"reply": f"❌ 分发模块错误：{str(e)}", "intent": intent_result}
