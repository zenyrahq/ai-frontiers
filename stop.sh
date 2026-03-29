#!/bin/bash

# AI Frontiers 停止脚本

echo "🛑 停止 AI Frontiers 开发环境..."

# 停止API服务
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "停止 API 服务..."
    pkill -f "uvicorn main:app"
fi

# 可选：停止数据库服务
# brew services stop postgresql@18
# brew services stop redis

echo "✅ 开发环境已停止"
