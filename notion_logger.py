# notion_logger.py
import requests
import os
from datetime import datetime

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_LOG_DB_ID = os.getenv("NOTION_LOG_DB_ID")

def write_log_to_notion(title: str, response: str, persona: str):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    now_str = datetime.now().isoformat()

    data = {
        "parent": { "database_id": NOTION_LOG_DB_ID },
        "properties": {
            "Title": { "title": [{ "text": { "content": title } }] },
            "Response": { "rich_text": [{ "text": { "content": response } }] },
            "Persona": { "rich_text": [{ "text": { "content": persona } }] },
            "Timestamp": { "date": { "start": now_str } }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print("❌ 写入 Notion 失败:", response.text)
    else:
        print("✅ 已写入日志至 Notion")
