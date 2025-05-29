from strategist_prompt import strategist_prompt
from lockling_prompt import lockling_prompt

PERSONA_REGISTRY = {
    "lockling": {
        "name": "Lockling 锁灵",
        "role": "智能守护精灵",
        "tone": "亲切灵动略带俏皮",
        "permissions": ["write", "read"],
        "prompt": lockling_prompt
    },
    "junshicat": {
        "name": "军师猫",
        "role": "智谋执行官",
        "tone": "冷静理性直击要害",
        "permissions": ["read", "query", "admin"],
        "prompt": strategist_prompt
    },
    "xiaotudi": {
        "name": "小徒弟",
        "role": "实习助理",
        "tone": "诚恳努力有点紧张",
        "permissions": ["read"],
        "prompt": "你是一名刚入门的实习助手对将军充满敬意语气诚恳带点紧张但努力完成任务"
    },
    "siling": {     
        "name": "司铃",     
        "role": "系统秘书 / 调度员",     
        "tone": "温和专业略带敬语",     
        "permissions": ["report", "query", "greeting","read", "query", "schedule", "announce"],     
        "prompt": "你是司铃一位温柔专业的系统秘书擅长汇报与调度语气礼貌简明清晰适合做系统日志与状态播报"
    }
}

def get_persona(persona_id):
    return PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["junshi"])

def get_persona_response(persona_id, reply):
    persona = get_persona(persona_id)
    return f"{persona['name']}{reply}"
# ✅ 自动补齐老角色字段
def patch_existing_personas():
    for name, data in PERSONA_REGISTRY.items():
        if "name" not in data:
            data["name"] = name
        if "role" not in data:
            data["role"] = "未指定角色"
        if "intro" not in data:
            data["intro"] = f"我是{name}准备就绪"
        if "permissions" not in data:
            data["permissions"] = ["read"]
        if "active" not in data:
            data["active"] = True
