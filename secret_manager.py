# secret_manager.py

import json
import uuid
from datetime import datetime

SECRET_FILE = "secret_state.json"

# ✅ 加载当前口令
def load_secret():
    try:
        with open(SECRET_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_secret", ""), data.get("last_updated", "")
    except FileNotFoundError:
        return "", ""

# ✅ 写入新口令
def generate_new_secret():
    new_secret = uuid.uuid4().hex[:8]  # 可更换为更安全的生成方式
    timestamp = datetime.now().isoformat()
    data = {
        "current_secret": new_secret,
        "last_updated": timestamp
    }
    with open(SECRET_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return new_secret

# ✅ 普通验证（永久口令验证）
def verify_secret(input_secret: str):
    current, _ = load_secret()
    return input_secret == current

# ✅ 临时验证 + 验证成功自动换口令（一次性验证模式）
def verify_and_invalidate_secret(input_secret: str):
    current, _ = load_secret()
    if input_secret == current:
        generate_new_secret()  # 验证通过即更新
        return True
    return False

# ✅ 获取当前口令信息（调试、日志等用途）
def get_current_secret_info():
    current, timestamp = load_secret()
    return {
        "current_secret": current,
        "last_updated": timestamp
    }
