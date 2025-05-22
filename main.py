from fastapi import FastAPI, Request
from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
from openai_helper import ask_gpt
from notion_helper import save_to_notion
from notion_persona_writer import save_log_to_notion
import json

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    # 获取原始输入
    data = await request.json()
    message = data.get("message")
    user_input_persona = data.get("persona", "junshi")

    # GPT 联合识别角色与行为意图
    recognition_prompt = f"""
用户说：“{message}”

请判断以下两点：
1. 这句话的行为意图（只选一项）：schedule, query, control, greeting, report, other
2. 用户想唤起哪个角色？从 ["junshi", "lockling", "siling", "xiaotudi"] 中选最接近的

只返回标准JSON格式：{{"intent": "...", "persona": "..."}}，不能解释说明。
"""

    intent_data_raw = await ask_gpt(recognition_prompt, PERSONA_REGISTRY["junshi"])
    intent_data = json.loads(intent_data_raw)

    intent = intent_data.get("intent", "other").lower().strip()
    persona_id = intent_data.get("persona", "lockling").lower().strip()

    # 获取角色信息
    persona = PERSONA_REGISTRY.get(persona_id, PERSONA_REGISTRY["lockling"])

    # 权限判断
    if not has_permission(persona_id, intent):
        reply = f"{persona['name']}：对不起，您无权执行 {intent} 操作。"
        await save_log_to_notion(persona["name"], message, reply)
        return {
            "reply": reply,
            "persona": persona["name"]
        }

    # GPT 回答生成
    reply = await ask_gpt(message, persona)

    # ✅ 写入 Notion 日志
    await save_log_to_notion(persona["name"], message, reply)

    # （可选）风格化回复输出
    styled_reply = get_persona_response(persona_id, reply)

    return {
        "reply": styled_reply,
        "persona": persona["name"]
    }
