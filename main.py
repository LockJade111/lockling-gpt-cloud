from fastapi import FastAPI, Request
from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
from openai_helper import ask_gpt
from notion_persona_writer import save_log_to_notion
from role_auto_register import register_from_intent  # 👈 自动注册系统导入
import json

app = FastAPI()

# ✅ GPT判断使用哪个角色（支持4个角色 + 动态注册）
from role_auto_register import register_from_intent  # 确保已导入

# ✅ GPT判断使用哪个角色（支持4个角色 + 动态注册）
async def identify_persona_from_message(message: str) -> str:
    lowered = message.lower()

    # 1. 关键词直接匹配已有角色
    if "司铃" in lowered or "秘书" in lowered:
        return "siling"
    if "军师猫" in lowered or "智谋执行官" in lowered:
        return "junshicat"
    if "军师" in lowered:
        return "junshi"
    if "锁灵" in lowered:
        return "lockling"
    if "徒弟" in lowered or "实习" in lowered:
        return "xiaotudi"

    # 2. 自动注册：如“安排小艾协助”“请派小张去做”
    import re
    match = re.search(r"(安排|请派)([^，。\s]{1,6})(协助|帮忙|去做)", message)
    if match:
        name = match.group(2).strip()
        print(f"[自动注册] 捕捉到新角色意图：{name}")
        return await register_from_intent(name)

    # 3. 否则交给 GPT 判断角色意图（留作未来备用）
    return ""
