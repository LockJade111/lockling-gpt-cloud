from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from persona_registry import PERSONA_REGISTRY, get_persona_response, patch_existing_personas
from dotenv import load_dotenv
import os
import openai
import uvicorn
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

patch_existing_personas()  # 修复老角色字段

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    persona: str = ""

# ---------- GPT 通用调用函数 ----------
# ✅ GPT 通用调用函数（适配 openai 1.x）
from openai import OpenAI
client = OpenAI()  # 新 SDK 初始化方式

async def ask_gpt(prompt: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是结构化语义识别助手，只返回严格 JSON 格式"},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        print("🧠 GPT 返回：", content)
        return json.loads(content)
    except Exception as e:
        print("❌ GPT调用失败：", e)
        return {"error": str(e)}
# ---------- GPT 抽取角色信息 ----------
async def gpt_extract_role(message: str) -> dict:
    prompt = f"""用户说：{message}
请判断是否需要注册一个新角色。
若是，请返回如下 JSON：
{{
  "name": "小张",
  "title": "客服",
  "new": true,
  "comment": "已识别新角色：小张（客服）"
}}
若非注册请求，请返回 {{}}"""
    return await ask_gpt(prompt)

# ---------- GPT 生命周期管理 ----------
async def gpt_extract_lifecycle(message: str) -> dict:
    prompt = f"""用户说：{message}
请判断是否包含角色状态管理（暂停、卸任、调岗），若有请提取如下 JSON：
{{
  "name": "小张",
  "action": "暂停", 
  "new_role": "客服主管", 
  "comment": "小张已暂停"
}}"""
    return await ask_gpt(prompt)

# ---------- 权限模板 ----------
ROLE_TEMPLATE = {
    "会计师": ["read", "record"],
    "客服": ["read", "query"],
    "助手": ["read", "query"],
    "执行官": ["read", "query", "schedule"],
    "军师": ["read", "query", "schedule", "other"]
}

# ---------- 意图识别 ----------
def identify_intent(message: str) -> str:
    if any(kw in message for kw in ["安排", "协助", "计划", "执行"]):
        return "schedule"
    if any(kw in message for kw in ["什么", "多少", "能否", "吗"]):
        return "query"
    return "other"

# ---------- 权限判断 ----------
def has_permission(persona_id: str, intent: str) -> bool:
    if persona_id not in PERSONA_REGISTRY:
        return False
    p = PERSONA_REGISTRY[persona_id]
    return p.get("active", True) and intent in p.get("permissions", [])

# ---------- 自动注册角色 ----------
async def register_from_message(message: str) -> str:
    data = await gpt_extract_role(message)
    if not data or "error" in data or not data.get("name"):
        print("[注册跳过] 未识别出角色：", data)
        return ""
    name = data["name"]
    title = data.get("title", "助手")
    perms = ROLE_TEMPLATE.get(title, ["read", "query"])

    if name not in PERSONA_REGISTRY:
        PERSONA_REGISTRY[name] = {
            "name": name,
            "role": title,
            "intro": data.get("comment", f"我是{name}，担任{title}。"),
            "permissions": perms,
            "active": True
        }
        print(f"✅ 注册新角色：{name}（{title}）")

    return name

# ---------- 生命周期操作 ----------
async def handle_lifecycle(message: str) -> str:
    data = await gpt_extract_lifecycle(message)
    if not data or "error" in data or not data.get("name"):
        return "⚠️ 未识别出有效的生命周期操作"

    name = data["name"]
    if name not in PERSONA_REGISTRY:
        return f"⚠️ 找不到角色：{name}"

    action = data.get("action")
    new_role = data.get("new_role")
    comment = data.get("comment")

    if action == "暂停":
        PERSONA_REGISTRY[name]["active"] = False
    elif action == "卸任":
        del PERSONA_REGISTRY[name]
    elif action == "转岗" and new_role:
        PERSONA_REGISTRY[name]["role"] = new_role
        PERSONA_REGISTRY[name]["permissions"] = ROLE_TEMPLATE.get(new_role, ["read"])
    return comment or f"{name} 状态更新完成"

# ---------- 主路由 ----------
@app.post("/chat")
async def chat(req: ChatRequest):
    msg = req.message.strip()
    persona = req.persona.strip()

    # Step 1：生命周期操作
    if any(kw in msg for kw in ["暂停", "卸任", "转岗", "离职"]):
        result = await handle_lifecycle(msg)
        return {"reply": f"系统：{result}", "persona": "system"}

    # Step 2：自动注册
    if not persona:
        persona = await register_from_message(msg)

    # Step 3：意图识别 + 权限判断
    intent = identify_intent(msg)
    if not has_permission(persona, intent):
        return {"reply": f"{persona or '系统'}：对不起，您无权执行 {intent} 操作。", "persona": persona or "system"}

    # Step 4：返回回复
    reply = f"[{intent}] 请求已由 {persona} 接收。"
    return {"reply": get_persona_response(persona, reply), "persona": persona}

# ---------- 本地测试 ----------
if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)
