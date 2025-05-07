#!/bin/bash

# Step 1: 清除中间文件和缓存
echo "🚮 Cleaning build artifacts and caches..."
rm -rf build/ dist/ rionid.egg-info/ __pycache__/ rionid/__pycache__/ rionidgui/__pycache__/

# Step 2: 添加文件到 Git
echo "📁 Staging source files..."
git add .

# Step 3: 提交改动
read -p "📝 Enter commit message: " msg
git commit -m "$msg"

# Step 4: 推送到 GitHub
echo "⬆️  Pushing to GitHub..."
git push origin master

echo "✅ Done."
