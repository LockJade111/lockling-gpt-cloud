# role_auto_register.py

from persona_registry import PERSONA_REGISTRY

def register_from_intent(intent_name: str):
    fallback_name = intent_name.strip().replace(" ", "")[:6]

    if fallback_name not in PERSONA_REGISTRY:
        PERSONA_REGISTRY[fallback_name] = {
            "name": fallback_name,
            "role": "未知角色",
            "tone": "普通",
            "permissions": ["read"],
            "prompt": f"你是 {fallback_name}，一个自动生成的助手角色，请保持简洁回应并记录。"
        }
        print(f"[AUTO-REGISTER] 已自动注册新角色：{fallback_name}")

    return fallback_name
