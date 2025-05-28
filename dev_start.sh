#!/bin/bash

echo "🧠 Lockling 项目本地启动 + Git 同步"

# 1. 进入项目根目录
cd "$(dirname "$0")"

# 2. 激活 Python 虚拟环境
source venv/bin/activate

# 3. 加载 .env 环境变量
export $(grep -v '^#' .env | xargs)

# 4. Git 状态检查
echo "🔍 检查 Git 状态..."
git status

# 5. 自动添加、提交并推送
echo "📦 Git 提交本地改动..."
git add .
git commit -m "🚀 Dev: 自动提交所有更新 @ $(date '+%Y-%m-%d %H:%M:%S')" || echo "⚠️ 没有新变动可提交"
git push origin main || echo "⚠️ Git 推送失败，请检查远程设置"

# 6. 启动主服务
echo "🚀 启动 main.py..."
python main.py
