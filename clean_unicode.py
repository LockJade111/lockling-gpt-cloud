import os

# 常见非法字符（控制符中文标点花括号全角引号等）
illegal_chars = [
    '\uFF0C', '\uFF1A', '\u3002', '\uFEFF', '\uFFFC', '\u200B',
    '\u300C', '\u300D',  # 『』
    '\u201C', '\u201D',  # 
    '\u2018', '\u2019',  # 
    '\u3001', '\u300A', '\u300B', '\u3010', '\u3011',
    '\u2028', '\u2029', '\u00A0'  # 隐藏断行空格类字符
]

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

def clean_all_py_files():
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                clean_file(os.path.join(root, file))

if __name__ == "__main__":
    clean_all_py_files()
