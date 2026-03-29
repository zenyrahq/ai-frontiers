# AI Frontiers 部署指南

## 🚀 快速部署到云服务器

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB RAM
- 至少 20GB 磁盘空间

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ai-frontiers.git
cd ai-frontiers

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的 API Keys

# 3. 部署
chmod +x deploy.sh
./deploy.sh
```

---

## 📋 详细配置

### 1. 环境变量配置

创建 `.env` 文件：

```bash
# Database
POSTGRES_USER=aifrontiers
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=aifrontiers

# Redis
REDIS_PASSWORD=your_redis_password

# API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_secret_key_here
```

### 2. SSL 证书配置

#### 使用 Let's Encrypt（推荐）

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/nginx/ssl/key.pem
```

#### 使用自签名证书（仅开发）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout deployment/nginx/ssl/key.pem \
  -out deployment/nginx/ssl/cert.pem
```

### 3. 启动服务

```bash
# 生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

---

## 🏗️ 架构说明

```
                    ┌─────────────────┐
                    │     Nginx       │
                    │   (Port 80/443) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Frontend │  │   API    │  │  Static  │
        │ (Next.js)│  │ (FastAPI)│  │  Files   │
        └──────────┘  └────┬─────┘  └──────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │PostgreSQL│ │  Redis   │ │  arXiv   │
        │ +pgvector│ │ (Cache)  │ │   API    │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 🔧 服务管理

### 常用命令

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart api

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api

# 进入容器
docker-compose -f docker-compose.prod.yml exec api bash

# 更新服务
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 数据备份

```bash
# 备份 PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U aifrontiers aifrontiers > backup.sql

# 恢复 PostgreSQL
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U aifrontiers aifrontiers
```

---

## 📊 监控和日志

### 查看服务状态

```bash
# 所有服务状态
docker-compose -f docker-compose.prod.yml ps

# 资源使用
docker stats
```

### 日志管理

```bash
# API 日志
docker-compose -f docker-compose.prod.yml logs -f api

# Nginx 访问日志
docker-compose -f docker-compose.prod.yml exec nginx \
  tail -f /var/log/nginx/access.log

# Nginx 错误日志
docker-compose -f docker-compose.prod.yml exec nginx \
  tail -f /var/log/nginx/error.log
```

---

## 🌐 云服务商部署

### AWS

```bash
# 1. 启动 EC2 实例 (推荐 t3.medium)
# 2. 配置安全组开放 80/443 端口
# 3. SSH 连接并安装 Docker
# 4. 运行部署脚本
```

### Google Cloud Platform

```bash
# 1. 创建 Compute Engine 实例
# 2. 配置防火墙规则
# 3. SSH 连接并部署
```

### DigitalOcean

```bash
# 1. 创建 Droplet (推荐 4GB RAM)
# 2. 选择 Docker 镜像
# 3. SSH 连接并部署
```

### Vercel + Railway（推荐用于快速部署）

```bash
# 前端部署到 Vercel
cd frontend
vercel --prod

# 后端部署到 Railway
railway login
railway init
railway up
```

---

## 🔒 安全建议

1. **更改默认密码**: 修改 `.env` 中的所有密码
2. **配置防火墙**: 只开放必要端口 (80, 443, 22)
3. **定期更新**: 定期更新 Docker 镜像和系统
4. **备份数据**: 设置自动备份策略
5. **监控日志**: 定期检查异常访问

---

## 📞 故障排除

### 常见问题

**1. 数据库连接失败**
```bash
# 检查 PostgreSQL 状态
docker-compose -f docker-compose.prod.yml ps postgres

# 查看日志
docker-compose -f docker-compose.prod.yml logs postgres
```

**2. API 无法启动**
```bash
# 检查环境变量
docker-compose -f docker-compose.prod.yml exec api env

# 检查依赖
docker-compose -f docker-compose.prod.yml exec api pip list
```

**3. 前端无法访问**
```bash
# 检查 Nginx 配置
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# 重新加载配置
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 📈 性能优化

### 数据库优化

```sql
-- 创建 pgvector 索引
CREATE INDEX ON contents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM contents ORDER BY embedding <=> '[...]'::vector;
```

### Redis 缓存

```bash
# 配置 Redis 内存限制
# 在 docker-compose.prod.yml 中添加:
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

---

**部署完成后访问:**
- 前端: https://yourdomain.com
- API 文档: https://yourdomain.com/api/docs
- 健康检查: https://yourdomain.com/health
