from check_permission import check_permission
from supabase_logger import write_log_to_supabase
from finance_helper import log_finance
from schedule_helper import schedule_event
from customer_helper import log_customer_info  # 新增

async def dispatch_intents(intent_result, message, persona):
    intent = intent_result["intent"]
    permission = intent_result.get("requires_permission", "")

    # 权限判断
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
                amount=0,  # 后续支持 GPT 金额提取
                category="收入",
                created_by=persona
            )
            return {"reply": "✅ 财务信息已记录", "intent": intent_result}

        elif intent == "schedule_service":
            await schedule_event(
                what="售后服务",  # 可扩展解析具体服务
                when="稍后",       # 可扩展识别时间
                by=persona
            )
            return {"reply": "✅ 售后已安排，司铃将跟进", "intent": intent_result}

        elif intent == "query_logs":
            return {"reply": "📜（伪）日志查询功能待接入 Supabase 查询接口", "intent": intent_result}

        elif intent == "grant_permission":
            return {"reply": "🔐（伪）权限已赋予，功能待接入角色表更新", "intent": intent_result}

        elif intent == "revoke_permission":
            return {"reply": "🛑（伪）权限已撤销，功能待接入角色表更新", "intent": intent_result}

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

        else:
            return {"reply": "🤔 未识别的操作，或暂未支持该指令", "intent": intent_result}

    except Exception as e:
        return {"reply": f"❌ 分发模块出错：{str(e)}", "intent": intent_result}
