import os
from dotenv import load_dotenv
from notion_client import Client
from persona_registry import PERSONA_REGISTRY

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = "1fb53c119201803281cec8d2d89b5f1f"

def write_personas_to_notion():
    for persona_id, data in PERSONA_REGISTRY.items():
        name = data.get("name", persona_id)
        role = data.get("role", "")
        tone = data.get("tone", "")
        permissions = data.get("permissions", [])
        prompt = data.get("prompt", "")

        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": name}}]},
                    "Role": {"rich_text": [{"text": {"content": role}}]},
                    "Tone": {"rich_text": [{"text": {"content": tone}}]},
                    "Permissions": {
                        "multi_select": [{"name": p} for p in permissions]
                    },
                    "Prompt": {"rich_text": [{"text": {"content": prompt}}]},
                }
            )
            print(f"✅ 写入成功：{name}")
        except Exception as e:
            print(f"❌ 写入失败：{name} | 错误：{str(e)}")

if __name__ == "__main__":
    write_personas_to_notion()
