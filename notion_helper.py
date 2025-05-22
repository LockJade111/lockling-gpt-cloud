import os
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
database_id = os.getenv("NOTION_DATABASE_ID")

async def save_to_notion(persona, question, answer):
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [
                        {"text": {"content": question[:100]}}  # 避免超长标题
                    ]
                },
                "Response": {
                    "rich_text": [
                        {"text": {"content": answer[:2000]}}  # 控制写入长度
                    ]
                },
                "Persona": {
                    "select": {"name": persona}
                },
                "Timestamp": {
                    "date": {
                        "start": datetime.utcnow().isoformat()
                    }
                }
            }
        )
    except Exception as e:
        print(f"[NOTION ERROR] {str(e)}")
