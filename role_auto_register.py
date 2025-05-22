# role_auto_register.py

from persona_registry import PERSONA_REGISTRY

def register_from_intent(name: str) -> str:
    try:
        # 基础注册逻辑：写入一个默认角色设定
        PERSONA_REGISTRY[name] = {
            "name": name,
            "role": "新注册角色",
            "tone": "温和、默认",
            "permissions": ["read", "schedule"],  # 默认包含调度权限
            "prompt": f"你是 {name}，一个刚刚诞生的 AI 助手，请根据用户指令开始服务。"
        }
        print(f"[注册成功] 新角色 {name} 已写入 PERSONA_REGISTRY")
        return name
    except Exception as e:
        print(f"[注册失败] {e}")
        return "junshicat"  # 若失败，返回军师猫兜底
