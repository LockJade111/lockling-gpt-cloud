import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(user_input: str, persona: str) -> dict:
    user_input = user_input.strip()

    # ✅ 特定授权句式（分段式触发）
    if "我要授权军师猫注册新角色" in user_input:
        return {
            "intent": "begin_auth",
            "intent_type": "begin_auth",  # <-- 新增
            "target": "军师猫",
            "source": user_input
        }

    if "我是将军" in user_input:
        return {
            "intent": "confirm_identity",
            "intent_type": "confirm_identity",  # <-- 新增
            "identity": "将军",
            "source": user_input
        }

    if "玉衡在手" in user_input:
        return {
            "intent": "confirm_secret",
            "intent_type": "confirm_secret",  # <-- 新增
            "secret": "玉衡在手",
            "source": user_input
        }

    # ✅ 一句话式授权识别（旧机制仍保留）
    if any(kw in user_input for kw in ["授权", "注册", "密钥", "口令"]):
        persona_match = re.search(r"我是(\S+)", user_input)
        grantee_match = re.search(r"授权(\S+?)注册", user_input)
        permission_match = "register_persona" if "注册新角色" in user_input else None
        secret_match = re.search(r"(?:密钥|口令)[为是:]?\s*([^\s；]*)", user_input)

        if persona_match and grantee_match and permission_match and secret_match:
            return {
                "intent": "grant_permission",
                "intent_type": "grant_permission",  # <-- 新增
                "persona": persona_match.group(1),
                "grantee": grantee_match.group(1),
                "permission": permission_match,
                "secret": secret_match.group(1),
                "source": user_input
            }

    # 默认无匹配意图
    return {
        "intent": "unknown",
        "intent_type": "unknown",  # <-- 防止空值报错
        "source": user_input
    }
