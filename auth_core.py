# auth_core.py

import os
import re

# 加载环境变量中的授权者和密钥
AUTH_GRANTER = os.getenv("AUTH_GRANTER", "天下我有")
AUTH_KEY = os.getenv("AUTH_KEY", "玉衡在手")

# 允许的我是谁口头声明语句
AUTHORIZED_CLAIMS = [
    "我是最高将领",
    "我是天下我有",
    "我是你唯一的指挥官",
    "听我号令",
    "我是掌令者",
    "我是主控",
]

# 密钥候选（可扩展）
VOICE_PASSPHRASES = [
    "玉衡在手",
    "玄武控印",
    "北辰主印",
    "锁玉之权",
]

def is_authorized_speaker(persona: str, message: str) -> bool:
    """
    判断当前 persona 是否为授权人本人或是否说出了强信任身份声明
    """
    if persona == AUTH_GRANTER:
        return True
    
    for phrase in AUTHORIZED_CLAIMS:
        if phrase in message:
            return True

    return False

def contains_valid_passphrase(message: str) -> bool:
    """
    判断口头中是否包含合法密钥短语
    """
    for key in VOICE_PASSPHRASES:
        if key in message:
            return True
    return False

def extract_passphrase(message: str) -> str:
    """
    从语句中提取口令（用于更新等）
    """
    for key in VOICE_PASSPHRASES:
        if key in message:
            return key
    return ""
