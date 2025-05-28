#!/bin/bash

echo "🧠 Lockling 项目本地启动 + Git 同步"

# Step 1: 加载环境变量
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✅ 已加载 .env 环境变量"
else
  echo "⚠️ 找不到 .env 文件，部分功能可能失效"
fi

# Step 2: 激活虚拟环境（可选）
if [ -d "venv" ]; then
  source venv/bin/activate
  echo "✅ 已激活虚拟环境"
else
  echo "⚠️ 未检测到 venv 虚拟环境"
fi

# Step 3: Git 提交本地变更
echo "📦 Git 提交本地改动..."
git add .
git commit -m "🚀 Dev: 自动提交所有更新 @ $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
git push origin main

# Step 4: 启动 main.py
echo "🚀 启动 main.py..."
python main.py
