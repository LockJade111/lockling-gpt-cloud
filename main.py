from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from persona_registry import PERSONA_REGISTRY, get_persona_response
from dotenv import load_dotenv
import os
import openai
import uvicorn
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# ---------- GPT语义解析辅助 ----------
async def ask_gpt(prompt: str) -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 可替换为 "gpt-4"
        messages=[
            {"role": "system", "content": "你是一个结构化语言解析助手。"},
            {"role": "user", "content": prompt}
        ]
    )
    content = response["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except:
        return {"error": "解析失败", "raw": content}

# ---------- 角色注册 GPT ----------
async def gpt_extract_role(message: str) -> dict:
    prompt = f"""从下面这句话中提取角色注册意图与信息。
用户可能会说“安排一个客服叫小美”或“我们需要一个会计师小张”等。

请以如下 JSON 格式返回：
{{
  "name": "小张",
  "title": "客服",
  "new": true,
  "comment": "识别为新角色：小张（客服）"
}}
如果无法识别，请返回空 JSON：{{}}

用户输入：{message}
"""
    return await ask_gpt(prompt)

# ---------- 生命周期操作 GPT ----------
async def gpt_extract_lifecycle(message: str) -> dict:
    prompt = f"""从下面的语言中识别是否涉及角色管理（暂停、卸任、转岗、替代），返回操作内容：

返回格式：
{{
  "name": "小张",
  "action": "暂停",  // 或 卸任 / 转岗 / 替代
  "new_role": "客服主管",
  "comment": "已暂停小张"
}}

用户输入：{message}
"""
    return await ask_gpt(prompt)

# ---------- 权限模板 ----------
ROLE_TEMPLATE = {
    "会计师": ["read", "record"],
    "客服": ["read", "query"],
    "助手": ["read", "query"],
    "执行官": ["read", "query", "schedule"],
    "军师": ["read", "query", "schedule", "other"],
}

# ---------- 意图识别 ----------
def identify_intent(message: str) -> str:
    if any(kw in message for kw in ["安排", "计划", "预定", "协助"]):
        return "schedule"
    if any(kw in message for kw in ["什么", "多少", "如何", "吗"]):
        return "query"
    if any(kw in message for kw in ["记录", "写入", "备份"]):
        return "write"
    return "other"

# ---------- 权限校验 ----------
def has_permission(persona_id: str, intent: str) -> bool:
    if persona_id not in PERSONA_REGISTRY:
        return False
    if not PERSONA_REGISTRY[persona_id].get("active", True):
        return False
    return intent in PERSONA_REGISTRY[persona_id].get("permissions", [])

# ---------- 注册角色 ----------
async def register_from_message(message: str) -> str:
    data = await gpt_extract_role(message)
    name = data.get("name")
    title = data.get("title")
    comment = data.get("comment", "")
    if not name or name in PERSONA_REGISTRY:
        return name  # 已存在或识别失败

    perms = ROLE_TEMPLATE.get(title, ["read", "query", "schedule"])
    PERSONA_REGISTRY[name] = {
        "name": name,
        "role": f"注册角色：{title}",
        "intro": comment,
        "permissions": perms,
        "active": True
    }
    return name

# ---------- 生命周期管理 ----------
async def handle_lifecycle(message: str) -> str:
    result = await gpt_extract_lifecycle(message)
    name = result.get("name")
    action = result.get("action")
    new_role = result.get("new_role")
    comment = result.get("comment")

    if not name or name not in PERSONA_REGISTRY:
        return f"⚠️ 找不到角色：{name}"

    if action == "暂停":
        PERSONA_REGISTRY[name]["active"] = False
    elif action == "卸任":
        del PERSONA_REGISTRY[name]
    elif action == "转岗" and new_role:
        PERSONA_REGISTRY[name]["role"] = new_role
        PERSONA_REGISTRY[name]["permissions"] = ROLE_TEMPLATE.get(new_role, ["read", "query"])
    return comment or f"{name} 已完成 {action}"

# ---------- 主路由 ----------
@app.post("/chat")
async def chat(req: ChatRequest):
    msg = req.message.strip()
    persona = req.persona.strip()
    
    # Step 1: 生命周期操作
    if any(x in msg for x in ["暂停", "卸任", "调岗", "转岗", "代理", "离职"]):
        result = await handle_lifecycle(msg)
        return {"reply": f"系统：{result}", "persona": "system"}

    # Step 2: 注册角色
    if not persona:
        name = await register_from_message(msg)
        if name:
            persona = name

    # Step 3: 意图识别与权限判断
    intent = identify_intent(msg)
    if not has_permission(persona, intent):
        return {"reply": f"{persona or '系统'}：对不起，您无权执行 {intent} 操作。", "persona": persona or "system"}

    # Step 4: 生成响应
    reply = f"已识别为指令 [{intent}]，由 [{persona}] 执行。"
    return {"reply": get_persona_response(persona, reply), "persona": persona}

# ---------- 本地运行 ----------
if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)
