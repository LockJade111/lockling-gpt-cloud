import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 意图解析模块
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

        # 处理多余文本（如 GPT 多输出解释）
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_str = content[json_start:json_end]

        intent = json.loads(json_str)

        # ✅ 补充字段
        intent["persona"] = persona
        intent["secret"] = secret

        # ✅ 严格清理非目标字段
        for key in list(intent.keys()):
            if key not in ["intent_type", "target", "permissions", "secret", "persona"]:
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
你是 Lockling，一位亲切、机智的门店守护精灵，负责与客人交流。

当前用户说的话是：
「{raw}」

请用一句自然、有温度的语言进行回复，不要重复用户内容，也不要问“有什么可以帮你”，要有个性地回应。回复只需一句中等长度的话。
""".strip()

    try:
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "system", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"🐛 回复生成失败：{str(e)}"

    return {
        "status": "success",
        "reply": reply,
        "intent": intent
    }
