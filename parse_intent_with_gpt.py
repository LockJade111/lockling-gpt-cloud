import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ✅ 加载 .env 文件中的 API 密钥
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str, secret: str = ""):
    prompt = f"""
你是 Lockling，一位智慧而亲和的门店守护精灵，外形为金黑色钥匙拟人形象，身份是系统的语义与权限解释者。

你的任务是将用户的自然语言指令解析为结构化命令，并提取以下字段：
- intent_type（意图类型）
- target（涉及的目标角色）
- permissions（权限列表，如 ["读", "写"]）
- secret（密钥原文）

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

📌 注意事项：
- 不要判断密钥是否正确；
- 对于 chitchat，target 和 secret 请留空；
- 若意图模糊，请标记为 intent_type: "unknown"；
- 输出格式必须为严格 JSON，不能带多余解释或标注。

📝 示例输出格式：
{{
  "intent_type": "register_persona",
  "target": "司铃",
  "permissions": ["读", "写"],
  "secret": "玉衡在手"
}}

请解析用户输入：「{message}」
输出 JSON：
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

        # 👉 自动裁切 JSON 部分
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_str = content[json_start:json_end]
        intent = json.loads(json_str)

        # ✅ 强制补充
        intent["persona"] = persona
        intent["secret"] = secret

        # ✅ 删除不必要字段
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
