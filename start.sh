#!/bin/bash

# AI Frontiers 快速启动脚本

echo "🚀 启动 AI Frontiers 开发环境..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查并启动PostgreSQL
if ! brew services list | grep -q "postgresql@18.*started"; then
    echo "${BLUE}启动 PostgreSQL...${NC}"
    brew services start postgresql@18
    sleep 2
fi

# 检查并启动Redis
if ! brew services list | grep -q "redis.*started"; then
    echo "${BLUE}启动 Redis...${NC}"
    brew services start redis
    sleep 1
fi

echo "${GREEN}✅ 数据库服务已启动${NC}"

# 激活虚拟环境并启动API
echo "${BLUE}启动 API 服务...${NC}"
cd api
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
