from persona_registry import PERSONA_REGISTRY

def has_permission(persona_id, action):
    persona = PERSONA_REGISTRY.get(persona_id)
    if not persona:
        return False
    return action in persona.get("permissions", [])
