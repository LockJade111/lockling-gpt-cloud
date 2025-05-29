import os
from notion_client import Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
db_id = os.getenv("NOTION_LOG_DB")

async def save_log_to_notion(message: str, persona: str, reply: str, intent: str):
    try:
        notion.pages.create(
            parent={"database_id": db_id},
            properties={
                "时间": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "用户请求": {
                    "title": [{"text": {"content": message}}]
                },
                "回复内容": {
                    "rich_text": [{"text": {"content": reply}}]
                },
                "角色": {
                    "rich_text": [{"text": {"content": persona}}]
                },
                "意图": {
                    "select": {"name": intent}
                }
            }
        )
        print("✅ 日志已写入 Notion")
    except Exception as e:
        print("❌ Notion 写入失败", str(e))
