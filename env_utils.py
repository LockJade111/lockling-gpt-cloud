import os

def read_env_file():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            return f.readlines()
    return []

def write_env_file(lines):
    env_path = ".env"
    with open(env_path, "w") as f:
        f.writelines(lines)

def update_env_variable(key: str, value: str, append_if_array=True):
    lines = read_env_file()
    updated = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            current = line.strip().split("=", 1)[1]
            if append_if_array:
                values = [v.strip() for v in current.split(",") if v.strip()]
                if value not in values:
                    values.append(value)
                new_value = ",".join(values)
            else:
                new_value = value
            new_lines.append(f"{key}={new_value}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key}={value}\n")

    write_env_file(new_lines)
    print(f"✅ .env 更新成功：{key} -> {value}")

def remove_from_env_array(key: str, value_to_remove: str):
    lines = read_env_file()
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            current = line.strip().split("=", 1)[1]
            values = [v.strip() for v in current.split(",") if v.strip() and v.strip() != value_to_remove]
            new_value = ",".join(values)
            new_lines.append(f"{key}={new_value}\n")
        else:
            new_lines.append(line)

    write_env_file(new_lines)
    print(f"🔻 .env 移除授权：{value_to_remove}")

# ✅ 示例：添加授权关系
def add_authorization_env(authorizer: str, grantee: str):
    pair = f"{authorizer}:{grantee}"
    update_env_variable("AUTHORIZED_REGISTER", pair)

# ✅ 示例：激活新 persona
def activate_persona(name: str):
    key = f"PERSONA_{name}"
    update_env_variable(key, "active", append_if_array=False)
