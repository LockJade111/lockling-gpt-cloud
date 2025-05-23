# 文件名: schedule_helper.py

def schedule_event(details: dict) -> str:
    return f"✅ 事件已安排：{details.get('what', '未知内容')}，时间：{details.get('when', '待定')}。"
