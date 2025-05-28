# secret_manager.py
import json
import uuid
from datetime import datetime

SECRET_FILE = "secret_state.json"

def load_secret():
    try:
        with open(SECRET_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_secret", ""), data.get("last_updated", "")
    except FileNotFoundError:
        return "", ""

def generate_new_secret():
    new_secret = uuid.uuid4().hex[:8]  # 可改为更优雅的样式，如 base58
    timestamp = datetime.now().isoformat()
    data = {
        "current_secret": new_secret,
        "last_updated": timestamp
    }
    with open(SECRET_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return new_secret

def verify_secret(input_secret: str):
    current, _ = load_secret()
    return input_secret == current
