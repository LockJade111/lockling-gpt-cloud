import os

# ⚠️ 你可以根据实际情况扩展这个字符列表
illegal_chars = ['\uFF0C', '\uFF1A', '\u3002', '\uFEFF', '\uFFFC', '\u200B']

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for ch in illegal_chars:
        if ch in content:
            content = content.replace(ch, '')
            print(f"✅ 清除非法字符 {repr(ch)} in {file_path}")

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            clean_file(os.path.join(root, file))
