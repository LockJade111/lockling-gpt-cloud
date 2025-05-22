from strategist_prompt import strategist_prompt
from lockling_prompt import lockling_prompt

PERSONA_REGISTRY = {
    "junshi": {
        "name": "军师",
        "prompt": strategist_prompt
    },
    "lockling": {
        "name": "Lockling",
        "prompt": lockling_prompt
    }
}

def get_persona(persona_id):
    return PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["junshi"])
