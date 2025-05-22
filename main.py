from fastapi import FastAPI, Request
from permission_checker import has_permission
from persona_registry import PERSONA_REGISTRY, get_persona_response
from openai_helper import ask_gpt
from notion_persona_writer import save_log_to_notion
from role_auto_register import register_from_intent  # 👈 自动注册系统导入
import json

app = FastAPI()

# ✅ GPT判断使用哪个角色（支持4个角色 + 动态注册）
async def identify_persona_from_message(message: str) -> str:
    prompt = f"""
当前系统中有四个角色，请判断用户这句话想唤起的是哪一个角色，并返回该角色的唯一 ID。角色如下：

1. 军师（ID：junshicat）：战略顾问、分析规划
2. 司铃（ID：siling）：智能秘书、调度安排
3. 锁灵（ID：lockling）：品牌精灵、宣传互动
4. 小徒弟（ID：xiaotudi）：初学者助手、协作引导

用户说：“{message}”

请只返回角色ID，例如 siling，不要解释，不加标点。
"""
    result = await ask_gpt(prompt, PERSONA_REGISTRY["junshicat"])
    return result.strip().lower()

# ✅ GPT判断行为意图（用于权限判断）
async def identify_intent(message: str) -> str:
    prompt = f"""
请判断这句话的行为意图，只输出以下六个之一：
- schedule（调度安排）
- query（问题咨询）
- report（信息上报）
- control（控制命令）
- greeting（问候打招呼）
- other（其他）

用户说：“{message}”
请只返回关键词，不解释。
"""
    result = await ask_gpt(prompt, PERSONA_REGISTRY["junshicat"])
    return result.strip().lower()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")

    # GPT识别角色ID
    persona_id = await identify_persona_from_message(message)

    # 🧠 自动注册新角色（如果未存在）
    if persona_id not in PERSONA_REGISTRY:
        print(f"⚠️ 未知角色 {persona_id}，尝试注册...")
        new_persona = await register_from_intent(message)
        if new_persona:
            PERSONA_REGISTRY[persona_id] = new_persona
            persona = new_persona
            print(f"✅ 角色 {persona_id} 注册成功")
        else:
            persona = PERSONA_REGISTRY["junshicat"]
            print(f"❌ 注册失败，默认切回军师")
    else:
        persona = PERSONA_REGISTRY[persona_id]

    # GPT判断行为意图
    intent = await identify_intent(message)

    # 权限判断
    if not has_permission(persona_id, intent):
        reply = f"{persona['name']}：对不起，您无权执行 {intent} 操作。"
        await save_log_to_notion(persona["name"], message, reply)
        return {"reply": reply, "persona": persona["name"]}

    # GPT生成回复
    reply = await ask_gpt(message, persona)

    # 写入日志
    await save_log_to_notion(persona["name"], message, reply)

    # 包装风格输出
    styled_reply = get_persona_response(persona_id, reply)

    return {
        "reply": styled_reply,
        "persona": persona["name"]
    }
