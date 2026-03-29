# 服务器配置与部署命令

> 在阿里云 ECS 服务器上执行的完整命令清单

---

## 第一部分：服务器环境配置

### 1. 更新系统

```bash
apt update && apt upgrade -y
```

### 2. 设置时区

```bash
timedatectl set-timezone Asia/Shanghai
```

### 3. 验证时区

```bash
date
```

### 4. 安装依赖包

```bash
apt install -y ca-certificates curl gnupg lsb-release git vim wget htop
```

### 5. 添加 Docker GPG 密钥

```bash
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### 6. 添加 Docker 仓库

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 7. 更新并安装 Docker

```bash
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 8. 启动 Docker 并设置开机自启

```bash
systemctl start docker
systemctl enable docker
```

### 9. 验证 Docker 安装

```bash
docker --version
docker compose version
```

### 10. 配置 Docker 镜像加速（国内镜像）

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://docker.anyhub.us.kg",
    "https://dockerhub.icu"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
```

### 11. 重启 Docker 生效

```bash
systemctl daemon-reload
systemctl restart docker
```

### 12. 配置防火墙

```bash
apt install -y ufw
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 13. 创建 Swap（4GB 内存建议配置）

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```

### 14. 创建项目目录

```bash
mkdir -p /root/ai-frontiers
cd /root/ai-frontiers
```

---

## 第二部分：上传项目代码

### 在本地电脑执行（打包项目）

```bash
cd /path/to/ai-frontiers
tar --exclude='node_modules' --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='.env' -czvf /tmp/ai-frontiers.tar.gz .
```

### 在本地电脑执行（上传到服务器）

```bash
scp /tmp/ai-frontiers.tar.gz root@<YOUR_SERVER_IP>:/root/
```

### 在服务器执行（解压项目）

```bash
cd /root
mkdir -p ai-frontiers
tar -xzvf ai-frontiers.tar.gz -C ai-frontiers
cd /root/ai-frontiers
ls
```

---

## 第三部分：配置环境变量

### 1. 创建环境配置文件（直接复制执行）

```bash
cat > /root/ai-frontiers/.env << 'EOF'
# 数据库配置
DATABASE_URL=postgresql://aifrontiers:AiFrontiers2024!@postgres:5432/aifrontiers
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis配置
REDIS_URL=redis://:RedisPass2024!@redis:6379/0
REDIS_PASSWORD=RedisPass2024!

# Elasticsearch配置（暂不使用）
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX_PREFIX=aifrontiers

# AI API Keys（可选，暂时留空）
# Anthropic API Key - 用于 Claude API（智能摘要、翻译）
# 获取地址: https://console.anthropic.com
ANTHROPIC_API_KEY=

# OpenAI API Key - 用于 GPT API（备选方案）
# 获取地址: https://platform.openai.com
OPENAI_API_KEY=

# 翻译服务
TRANSLATION_SERVICE=claude

# 环境配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# 安全配置（稍后自动生成）
SECRET_KEY=will_be_generated

# 爬虫配置
CRAWLER_INTERVAL_MINUTES=15
CRAWLER_MAX_RETRIES=3
CRAWLER_TIMEOUT=30

# 推荐系统配置
RECOMMENDATION_CACHE_TTL=900
RECOMMENDATION_TOP_K=20

# 监控配置
ENABLE_METRICS=false
ENABLE_TRACING=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 外部服务
SENTRY_DSN=
SLACK_WEBHOOK_URL=

# 前端配置
NEXT_PUBLIC_API_URL=http://<YOUR_SERVER_IP>/api
NEXT_PUBLIC_APP_URL=http://<YOUR_SERVER_IP>
EOF
```

### 2. 生成并更新 SECRET_KEY

```bash
SECRET_KEY=$(openssl rand -hex 32) && sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" /root/ai-frontiers/.env
```

### 3. 验证配置文件

```bash
cat /root/ai-frontiers/.env
```

---

## API Key 说明

### API Key 用途

| Key | 用途 | 获取地址 |
|-----|------|----------|
| **Anthropic API Key** | 调用 Claude API（智能摘要、翻译） | https://console.anthropic.com |
| **OpenAI API Key** | 调用 GPT API（备选方案） | https://platform.openai.com |

### 是否必须配置？

**不是必须的**，项目基本功能可以正常运行：

| 功能 | 需要 API Key |
|------|-------------|
| 论文爬取和存储 | ❌ 不需要 |
| 搜索功能 | ❌ 不需要 |
| 前端展示 | ❌ 不需要 |
| 分类浏览 | ❌ 不需要 |
| 智能摘要生成 | ✅ 需要 |
| 多语言翻译 | ✅ 需要 |
| 智能推荐 | ✅ 需要 |

### 后续配置 API Key

如果以后需要，获取 Key 后执行：

```bash
nano /root/ai-frontiers/.env
# 找到 ANTHROPIC_API_KEY= 或 OPENAI_API_KEY= 填入
# Ctrl+O 保存，Ctrl+X 退出

# 重启服务生效
docker compose -f docker-compose.prod.yml restart api
```

---

## 第四部分：部署项目

### 1. 拉取基础镜像

```bash
cd /root/ai-frontiers
docker compose -f docker-compose.prod.yml pull
```

### 2. 构建项目镜像

```bash
docker compose -f docker-compose.prod.yml build
```

### 3. 启动所有服务

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 4. 查看服务状态

```bash
docker compose -f docker-compose.prod.yml ps
```

### 5. 查看日志

```bash
docker compose -f docker-compose.prod.yml logs -f
```

### 6. 健康检查

```bash
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost
```

---

## 第五部分：访问验证

### 浏览器访问

```
前端页面: http://<YOUR_SERVER_IP>
API 文档: http://<YOUR_SERVER_IP>/api/docs
健康检查: http://<YOUR_SERVER_IP>/health
```

---

## 常用运维命令

### 查看容器状态

```bash
docker ps
docker compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 所有服务日志
docker compose -f docker-compose.prod.yml logs -f

# 单个服务日志
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres
```

### 重启服务

```bash
# 重启所有服务
docker compose -f docker-compose.prod.yml restart

# 重启单个服务
docker compose -f docker-compose.prod.yml restart api
```

### 停止服务

```bash
docker compose -f docker-compose.prod.yml down
```

### 启动服务

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 进入容器

```bash
# 进入 API 容器
docker compose -f docker-compose.prod.yml exec api bash

# 进入数据库容器
docker compose -f docker-compose.prod.yml exec postgres bash
```

### 运行爬虫获取数据

```bash
docker compose -f docker-compose.prod.yml exec api bash
python scripts/fetch_arxiv.py
exit
```

---

## 系统监控命令

### CPU 和内存

```bash
htop
```

### 磁盘空间

```bash
df -h
```

### 内存使用

```bash
free -h
```

### 网络连接

```bash
netstat -tlnp
```

### Docker 资源使用

```bash
docker stats
```

---

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs api

# 检查配置
docker compose -f docker-compose.prod.yml config
```

### 端口被占用

```bash
# 查看端口占用
netstat -tlnp | grep 8000

# 杀掉进程
kill -9 <PID>
```

### 清理 Docker 资源

```bash
# 清理未使用的镜像、容器、网络
docker system prune -a
```

---

## 服务器信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | `<YOUR_SERVER_IP>` |
| 操作系统 | Ubuntu 22.04 |
| Docker 版本 | 29.3.1 |
| 项目目录 | /root/ai-frontiers |

---

**文档版本**: 1.1
**更新日期**: 2026-03-27
