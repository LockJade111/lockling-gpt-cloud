import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_intent(message: str, persona: str):
    # 注入当前身份 context
    persona_intro = f"你现在以 {persona} 的身份处理指令。身份等级将影响你是否有权限执行某些操作。\n\n"

    prompt = persona_intro + """
你是一个权限与语义解析系统，负责将用户发出的自然语言命令，转换为结构化意图。

系统中有多种身份（persona），例如：
🟢 persona="将军"：系统最高权限者，可注册、授权、撤销、删除等敏感操作，需提供密钥（如“玉衡在手”）。
🟡 persona="司铃"、"小助手" 等：默认无注册/授权权限，需被“将军”授权后才可操作。

你需识别以下意图类型（intent_type）：

1. confirm_secret       → 身份验证，如 “口令是玉衡在手”
2. register_persona     → 注册角色，如 “我要注册角色 小助手”
3. confirm_identity     → 授权他人，如 “我要授权 司铃 注册权限”
4. revoke_identity      → 取消授权，如 “我要取消 司铃 的注册权限”
5. delete_persona       → 删除角色，如 “我要删除角色 小助手”
6. authorize            → 授权他人权限（简略指令，如 “授权小艾只读”）
7. unknown              → 其他无法识别或无权限的内容

---

【示例】：

- “口令是玉衡在手” → confirm_secret
- “我要注册角色 小助手，口令是玉衡在手” → register_persona
- “我要授权 司铃 注册权限” → confirm_identity
- “授权小艾只读” → authorize
- “你好” → unknown

---

【输出格式要求（仅 JSON，无注释）】：

{
  "intent_type": "...",
  "target": "...",
  "permissions": [...],
  "secret": "...",
  "allow": true/false,
  "reason": "..."
}

---

【用户输入】：
""" + message.strip()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    result = response.choices[0].message.content.strip()

    try:
        return json.loads(result)
    except Exception as e:
        return {
            "intent_type": "parse_error",
            "message": message,
            "raw": result,
            "error": str(e)
        }
你是一个智能意图识别系统，需从用户输入中提取以下字段：

- intent_type（指令类型）
- persona（操作者）
- target（目标角色）
- secret（密钥）
- permissions（权限列表）

支持的 intent_type 有：
- confirm_secret：确认密钥，如“我是将军，密钥是玉衡在手”
- confirm_identity：确认身份，如“我是司铃”
- create_persona：创建新角色，如“我要一个叫小美的角色”
- delete_persona：删除角色，如“删掉李雷”
- update_permission：授权角色某项权限
- query_logs：查询日志
- unknown：无法判断

---

以下是示例（Few-shot）：

用户输入：
> 我是将军，口令是玉衡在手，我要创建一个叫小美的角色

输出结构：
{
  "intent_type": "create_persona",
  "persona": "将军",
  "secret": "玉衡在手",
  "target": "小美"
}

---

用户输入：
> 玉衡能不能查预算？

输出结构：
{
  "intent_type": "update_permission",
  "persona": "将军",
  "target": "玉衡",
  "permissions": ["预算查询"]
}

---

用户输入：
> 司铃 删除李雷

输出结构：
{
  "intent_type": "delete_persona",
  "persona": "司铃",
  "target": "李雷"
}

---

用户输入：
> 谁能查日志？

输出结构：
{
  "intent_type": "query_logs",
  "persona": "",
  "target": "",
  "permissions": []
}
