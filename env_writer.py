def update_env_key_in_file(new_key: str):
    path = ".env"
    with open(path, "r") as f:
        lines = f.readlines()

    with open(path, "w") as f:
        for line in lines:
            if line.startswith("AUTH_KEY="):
                f.write(f"AUTH_KEY={new_key}\n")
            else:
                f.write(line)
