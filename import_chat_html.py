import sqlite3
from bs4 import BeautifulSoup

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

with open('chat.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

messages = soup.find_all("div", class_="message-text")

for i, msg in enumerate(messages):
    text = msg.get_text(strip=True)
    cursor.execute('INSERT INTO memory (content, source, trust_level) VALUES (?, ?, ?)',
                   (text, 'chat.html', 3))

conn.commit()
conn.close()
print(f'✅ 成功导入 {len(messages)} 条记录。')
