import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from generate_reply_with_gpt import handle_chitchat

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 解析意图
def parse_intent(message: str, persona: str, secret: str = ""):
    prompt = f"""
你是 Lockling，一位智慧而亲和的门店守护精灵，外形为金黑色钥匙拟人形象，身份是系统的语义与权限解释者。

你的任务是将用户的自然语言指令解析为结构化命令，并提取以下四个字段：
- intent_type
- target
- permissions
- secret

当前 persona：{persona}
当前密钥输入：{secret}

你支持的 intent_type 包括：
1. confirm_secret       → 身份验证
2. register_persona     → 注册角色
3. confirm_identity     → 授权他人
4. revoke_identity      → 取消授权
5. delete_persona       → 删除角色
6. authorize            → 授权权限
7. update_secret        → 更改密钥
8. chitchat             → 闲聊（你好、在吗、谢谢等）
9. unknown              → 无法识别

📌 说明：
- 不判断密钥是否正确；
- 若意图模糊，intent_type 设为 "unknown"；
- 对于 chitchat，不要填写 target 和 secret；
- 输出必须是合法 JSON，不能有解释文字。

📝 JSON格式示例：
{{
  "intent_type": "register_persona",
  "target": "司铃",
  "permissions": ["读", "写"],
  "secret": "玉衡在手"
}}

请解析以下用户输入，并输出 JSON：
「{message}」
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        content = response.choices[0].message.content.strip()

        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_str = content[json_start:json_end]

        intent = json.loads(json_str)

        # ✅ 补充字段
        intent["persona"] = persona
        intent["secret"] = secret

        # ✅ 严格清理非目标字段
        for key in list(intent.keys()):
            if key not in ["intent_type", "target", "permissions", "secret", "persona", "raw_message"]:
                intent.pop(key)

        return intent

    except Exception as e:
        return {
            "intent_type": "unknown",
            "persona": persona,
            "secret": secret,
            "target": "",
            "permissions": [],
            "reason": f"GPT解析异常：{str(e)}",
            "raw": content if 'content' in locals() else "无返回"
        }

# ✅ 闲聊意图处理模块（GPT生成自然语言回复）
def handle_chitchat(intent):
    print("📥 收到意图：chitchat")
    raw = intent.get("raw_message", "").strip()

    prompt = f"""
你是 Lockling，一位智慧又可靠的门店守护精灵。客人刚刚说：
「{raw}」

请用一句自然、有亲和力的中文回答，避免重复用户内容，不要说“我在”或“有什么可以帮你”，而是主动接话或回应。回复控制在20字以内，带点角色感。
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()
        print("🎯 GPT 回复内容：", reply)
    except Exception as e:
        reply = f"🐛 回复失败：{str(e)}"

    return {
        "status": "success",
        "reply": reply,
        "intent": intent
    }

# ✅ 主控分发器（根据 intent_type 分发到不同处理函数）
def intent_dispatcher(intent):
    intent_type = intent.get("intent_type", "")

    if intent_type == "chitchat":
        return handle_register(intent)
    elif intent_type == "authorize":
        return handle_authorize(intent)
    elif intent_type == "confirm_identity":
        return handle_confirm_identity(intent)
    elif intent_type == "confirm_secret":
        return handle_confirm_secret(intent)
    elif intent_type == "update_secret":
        return handle_update_secret(intent)
    elif intent_type == "revoke_identity":
        return handle_revoke_identity(intent)
    elif intent_type == "delete_persona":
        return handle_delete_persona(intent)
    elif intent_type == "chitchat":
        return handle_chitchat(intent)
    else:
        return {
            "status": "fail",
            "reply": f"❓ 无法识别的指令类型: {intent_type}",
            "intent": intent
        }

# 供外部模块 import 使用
__all__ = ["intent_dispatcher"]
