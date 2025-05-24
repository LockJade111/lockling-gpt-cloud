from pathlib import Path

# ✅ 使用绝对路径读取 .env，避免路径不一致导致空值
env_path = Path(__file__).resolve().parent / ".env"

# ✅ 精确读取 .env 中变量
def read_env_key_strict(key):
    if not env_path.exists():
        return ""
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                return line.strip().split("=", 1)[1].strip()
    return ""

# ✅ 最终保留函数：密钥匹配（如 SECRET_将军=玉衡在手）
def check_secret_permission(persona: str, secret: str):
    key = f"SECRET_{persona}"
    stored = read_env_key_strict(key)
    print(f"[🔐] 密钥验证：persona={persona}，输入密钥={secret}，系统密钥={stored}")
    return secret == stored
