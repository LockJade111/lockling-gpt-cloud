def write_log_to_supabase(query, reply, intent_result, status="success", source="production", raw_intent=None):
    supabase.table("logs").insert({
        "query": query,
        "reply": reply,
        "intent_result": intent_result,
        "status": status,
        "source": source,
        "raw_intent": raw_intent
    }).execute()
