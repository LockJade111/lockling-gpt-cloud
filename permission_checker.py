def has_permission(persona_id, action):
    from persona_registry import PERSONA_REGISTRY
    persona = PERSONA_REGISTRY.get(persona_id)
    if not persona:
        return False
    return action in persona.get("permissions", [])
if not has_permission(persona_id, "schedule"):
    return {"reply": f"{persona['name']}：对不起，您无权执行此操作。", "persona": persona["name"]}
