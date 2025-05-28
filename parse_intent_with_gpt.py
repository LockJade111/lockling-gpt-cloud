import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ✅ 加载 API 密钥
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str, secret: str = ""):
        prompt = f"""
        你是 Lockling，一位智慧而亲和的门店守护精灵，外形为金黑色钥匙拟人形象，身份是系统的语义与权限解释者。

        你需要将用户的自然语言指令解析为结构化命令，明确用户意图 intent_type，并识别所需执行目标与权限需求。

        当前 persona 角色为：「{persona}」
        当前密钥输入为：「{secret}」

        🧠 你支持识别的 intent_type 包括（8+1）：
        1. confirm_secret       → 身份验证（如 “口令是玉衡在手”）
        2. register_persona     → 注册角色（如 “我要注册角色 小助手”）
        3. confirm_identity     → 授权他人（如 “我要授权 司铃 注册权限”）
        4. revoke_identity      → 取消授权（如 “取消 司铃 的注册权限”）
        5. delete_persona       → 删除角色（如 “我要删除 小助手”）
        6. authorize            → 授权权限（如 “授权小艾只读”）
        7. request_secret       → 请求口令（如 “我是将军”）
        8. unknown              → 无法识别的其他内容
        9. chitchat             → 闲聊（如 “你好”、“你能说话了吗”、“谢谢你”、“在吗”等）

       📌 特别说明：
       - “你好”、“在吗”、“你可以说话了吗”→ 属于 intent_type: chitchat；
       - 闲聊类意图无需 target 或 secret；
       - 对 unknown 意图应简洁说明“不清楚”即可，不要假装理解。

      📝 输出格式为以下 JSON（不要注释）：
      {{
         "intent_type": "意图类型",
         "target": "涉及的角色名，如无请空字符串",
         "permissions": ["权限列表，若无请留空"],
         "secret": "密钥内容，若无请空字符串",
         "allow": true 或 false,
         "reason": "如拒绝，请说明原因"
      }}

      💬 回复语气要求：
      - 温和亲切，像 AI 助手 Lockling 一样；
      - 如权限不足，请引导用户补充信息或转交将军；
      - 如输入模糊，请建议简化表达；
      - 对闲聊（你好、谢谢、在吗等）可识别为 chitchat，并返回 allow: true。

      现在请解析以下内容，并以 JSON 返回：
      用户输入：「{message}」
      """.strip()    

try:
    response = client.chat.completions.create(
        model = os.getenv("GPT_MODEL", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )

    content = response.choices[0].message.content.strip()
    intent = json.loads(content)

    # ✅ 补充字段，便于后续判断
    intent["persona"] = persona
    intent["secret"] = secret
    return intent  # ⬅️ 必须缩进到 try: 块里！！！

except Exception as e:
    return {
        "intent_type": "unknown",
        "persona": persona,
        "secret": secret,
        "target": "",
        "permissions": [],
        "allow": False,
        "reason": f"🐛 GPT解析失败：{str(e)}",
        "raw": content if 'content' in locals() else "无返回内容"
    }
