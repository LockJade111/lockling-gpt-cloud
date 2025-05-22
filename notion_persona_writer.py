import os
from dotenv import load_dotenv
from notion_client import Client
from persona_registry import PERSONA_REGISTRY
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
notion = Client(auth=os.environ["NOTION_TOKEN"])

# ✅ 角色注册函数
def write_personas_to_notion():
    for persona_id, data in PERSONA_REGISTRY.items():
        name = data.get("name", "")
        role = data.get("role", "")
        tone = data.get("tone", "")
        permissions = ", ".join(data.get("permissions", []))
        prompt = data.get("prompt", "")

        try:
            notion.pages.create(
                parent={"database_id": os.environ["NOTION_ROLE_DB"]},
                properties={
                    "Name": {"title": [{"text": {"content": name}}]},
                    "Role": {"rich_text": [{"text": {"content": role}}]},
                    "Tone": {"rich_text": [{"text": {"content": tone}}]},
                    "Permissions": {"rich_text": [{"text": {"content": permissions}}]},
                    "Prompt": {"rich_text": [{"text": {"content": prompt}}]}
                }
            )
            print(f"✅ 写入成功：{name}")
        except Exception as e:
            print(f"❌ 写入失败：{name} | 错误：{str(e)}")

# ✅ 行为日志写入函数（注意是异步 async）
async def save_log_to_notion(persona_name: str, message: str, reply: str):
    try:
        notion.pages.create(
            parent={"database_id": os.environ["NOTION_LOG_DB"]},
            properties={
                "Title": {
                    "title": [{"text": {"content": message}}]
                },
                "Response": {
                    "rich_text": [{"text": {"content": reply}}]
                },
                "Persona": {
                    "select": {"name": persona_name}
                },
                "Timestamp": {
                    "date": {"start": datetime.utcnow().isoformat()}
                }
            }
        )
        print(f"✅ 行为日志写入成功：{persona_name}")
    except Exception as e:
        print(f"❌ 日志写入失败：{str(e)}")
