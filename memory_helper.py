# memory_helper.py

def save_memory(intent, persona=None):
    source = intent.get("source", "")
    print(f"📌 Save memory from {persona or '未知身份'}: {source}")
    # 实际记忆存储逻辑可另做
    return {"reply": f"🧠 已记住这句话：{source}"}
