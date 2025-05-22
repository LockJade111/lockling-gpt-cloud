# role_auto_register.py

from persona_registry import PERSONA_REGISTRY

def register_from_intent(name: str) -> str:
    try:
        # 基础注册逻辑：写入一个默认角色设定
        PERSONA_REGISTRY[name] = {
    "name": name,
    "role": "新注册角色",
    "tone": "温和、默认",
    "permissions": ["read", "schedule"],  # 加上 schedule 权限
    "prompt": f"你是 {name}，一个刚刚诞生的 AI 助手，请根据用户指令开始服务。"
}
