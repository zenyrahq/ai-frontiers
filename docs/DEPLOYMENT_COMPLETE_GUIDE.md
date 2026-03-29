# AI Frontiers 生产环境部署完整指南

> 基于阿里云 ECS 的完整部署流程记录

---

## 目录

1. [概述](#1-概述)
2. [阿里云账号注册与服务器购买](#2-阿里云账号注册与服务器购买)
3. [连接服务器](#3-连接服务器)
4. [服务器环境配置](#4-服务器环境配置)
5. [项目部署](#5-项目部署)
6. [常见问题与解决方案](#6-常见问题与解决方案)
7. [日常运维](#7-日常运维)

---

## 1. 概述

### 1.1 项目信息

| 项目 | 信息 |
|------|------|
| 项目名称 | AI Frontiers - AI前沿信息收集平台 |
| 服务器 IP | `<YOUR_SERVER_IP>` |
| 操作系统 | Ubuntu 22.04 64位 |
| Docker 版本 | 29.3.1 |
| 项目目录 | /root/ai-frontiers |

### 1.2 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (80/443)                        │
│                 反向代理 + 负载均衡                        │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│   Frontend (Next.js)    │  │    API (FastAPI)        │
│      Port: 3000         │  │      Port: 8000         │
└─────────────────────────┘  └───────────┬─────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
           ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
           │  PostgreSQL    │   │     Redis      │   │   NLP Service  │
           │   Port: 5432   │   │   Port: 6379   │   │  (Embedding)   │
           └────────────────┘   └────────────────┘   └────────────────┘
```

### 1.3 访问地址

| 服务 | 地址 |
|------|------|
| 前端首页 | `http://<YOUR_SERVER_IP>` |
| API 文档 | `http://<YOUR_SERVER_IP>/docs` |
| API ReDoc | `http://<YOUR_SERVER_IP>/redoc` |
| 健康检查 | `http://<YOUR_SERVER_IP>/health` |

---

## 2. 阿里云账号注册与服务器购买

### 2.1 注册阿里云账号

#### 步骤 1：访问官网
```
https://www.aliyun.com
```

#### 步骤 2：注册账号
1. 点击右上角 **"免费注册"**
2. 选择注册方式：
   - 手机号注册（推荐）
   - 邮箱注册
3. 填写手机号/邮箱
4. 获取并输入验证码
5. 设置密码（8-20个字符，包含字母和数字）

#### 步骤 3：实名认证（必须）
⚠️ **重要**：购买服务器必须完成实名认证

**个人认证流程：**
1. 登录阿里云控制台
2. 点击右上角头像 → 实名认证
3. 选择 "个人认证"
4. 填写真实姓名和身份证号
5. 选择认证方式：
   - 人脸识别（推荐，即时完成）
   - 阿里云 App 扫码
6. 完成认证

#### 步骤 4：充值账户
```
控制台 → 费用 → 充值
支持方式：支付宝、银行卡、网银
建议首次充值：¥100-200
```

### 2.2 购买 ECS 云服务器

#### 步骤 1：进入购买页面
```
方式1: 控制台 → 云服务器 ECS → 创建实例
方式2: 产品页 → 云服务器 ECS → 立即购买
```

#### 步骤 2：选择付费模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **包年包月** | 预付费，更便宜 | 长期稳定使用（推荐） |
| 按量付费 | 后付费，按小时计费 | 测试、临时使用 |

**推荐**: 包年包月，1年享85折

#### 步骤 3：选择地域和可用区

```
推荐配置:
- 地域: 华东1（杭州）或 华东2（上海）
- 可用区: 随机分配 或 选择主可用区
```

| 地域 | 适用用户 | 网络延迟 |
|------|----------|----------|
| 华东1（杭州） | 长三角用户 | 低 |
| 华东2（上海） | 长三角用户 | 低 |
| 华北2（北京） | 北方用户 | 低 |
| 华南1（深圳） | 南方用户 | 低 |

#### 步骤 4：选择实例规格

**推荐配置：**

| 规格 | vCPU | 内存 | 适用场景 | 月费用 |
|------|------|------|----------|--------|
| ecs.t5-c1m2.large | 2 | 4GB | **推荐本项目** | ~¥80 |
| ecs.c6.large | 2 | 4GB | 计算型，性能更好 | ~¥150 |

#### 步骤 5：选择镜像

```
镜像类型: 公共镜像
操作系统: Ubuntu
版本: Ubuntu 22.04 64位
```

**为什么选 Ubuntu 22.04?**
- LTS 长期支持版本（支持到 2027 年）
- Docker 兼容性最好
- 社区文档丰富

#### 步骤 6：选择存储

```
系统盘:
- 类型: ESSD 云盘（推荐）
- 大小: 40GB（免费）
- 性能: PL0

建议: 初期使用 40GB 系统盘足够
```

#### 步骤 7：选择网络和安全组

**网络配置：**
```
☑ 专有网络 VPC（推荐）
VPC: 默认 VPC
交换机: 默认交换机
公网 IP: 分配
带宽计费: 按固定带宽
带宽: 5 Mbps
```

**安全组配置：**
```
☑ 自动创建安全组
☑ 开放 HTTP(80) 端口
☑ 开放 HTTPS(443) 端口
☑ 开放 SSH(22) 端口
```

#### 步骤 8：设置登录凭证

```
登录方式:
  ☑ 自定义密码（推荐）

用户名: root
密码: [你的安全密码]

⚠️ 密码要求:
- 8-30 个字符
- 包含大写字母
- 包含小写字母
- 包含数字
- 包含特殊符号 (!@#$%^&* 等)
```

#### 步骤 9：确认订单

1. 检查配置信息
2. 勾选 "我已阅读并同意《云服务器 ECS 服务条款》"
3. 点击 "确认订单"
4. 完成支付

#### 步骤 10：等待实例创建

```
创建时间: 约 1-3 分钟
状态: 从 "创建中" 变为 "运行中"

记录以下信息:
- 实例 ID: i-xxxxxxxxxxxxxxx
- 公网 IP: <YOUR_SERVER_IP>
- 内网 IP: 172.x.x.x
```

### 2.3 费用说明

#### 包年包月价格

| 配置 | vCPU | 内存 | 带宽 | 月费用 | 年费用 |
|------|------|------|------|--------|--------|
| ecs.t5-c1m2.large | 2 | 4GB | 5M | ~¥80 | ~¥800 |
| ecs.c6.large | 2 | 4GB | 5M | ~¥150 | ~¥1500 |

#### 新用户优惠

```
新用户专享:
- ecs.t5-c1m2.large (2核4G): ¥99/年
- ecs.c6.large (2核4G): ¥199/年
- 限购 1-3 台
- 限首购
```

---

## 3. 连接服务器

### 3.1 获取连接信息

```
控制台 → 云服务器 ECS → 实例列表

找到你的实例，记录:
- 公网 IP 地址: <YOUR_SERVER_IP>
- 实例 ID
- 实例状态: 运行中
```

### 3.2 方式一：阿里云 Workbench（推荐新手）

```
1. 在实例列表，点击 "远程连接"
2. 选择 "通过 Workbench 远程连接"
3. 输入用户名: root
4. 输入密码: 你设置的密码
5. 点击 "确定"
```

### 3.3 方式二：Mac/Linux 终端 SSH

#### 基本连接
```bash
ssh root@<YOUR_SERVER_IP>
```

#### 使用密钥连接（更安全）

**步骤 1：创建密钥对**
```bash
# 在本地电脑生成密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 提示输入文件位置，直接回车使用默认
# ~/.ssh/id_rsa      # 私钥（保密）
# ~/.ssh/id_rsa.pub  # 公钥（上传到服务器）
```

**步骤 2：上传公钥到服务器**
```bash
# 方式1: 使用 ssh-copy-id
ssh-copy-id -i ~/.ssh/id_rsa.pub root@<YOUR_SERVER_IP>

# 方式2: 手动复制
ssh root@<YOUR_SERVER_IP>
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# 粘贴公钥内容，保存退出
chmod 600 ~/.ssh/authorized_keys
```

**步骤 3：使用密钥登录**
```bash
ssh -i ~/.ssh/your_key.pem root@<YOUR_SERVER_IP>
```

### 3.4 配置 SSH 快捷方式

```bash
# 编辑本地 SSH 配置
nano ~/.ssh/config

# 添加以下内容
Host aifrontiers
    HostName <YOUR_SERVER_IP>
    User root
    IdentityFile ~/.ssh/your_key.pem

# 保存后可以直接使用
ssh aifrontiers
```

### 3.5 文件上传/下载

#### 使用 SCP

```bash
# 上传文件
scp -i ~/.ssh/your_key.pem /本地文件路径 root@<YOUR_SERVER_IP>:/远程路径

# 下载文件
scp -i ~/.ssh/your_key.pem root@<YOUR_SERVER_IP>:/远程文件路径 /本地路径

# 上传目录
scp -i ~/.ssh/your_key.pem -r /本地目录 root@<YOUR_SERVER_IP>:/远程路径
```

#### 使用 Rsync（推荐）

```bash
# 同步目录（增量传输）
rsync -avz -e "ssh -i ~/.ssh/your_key.pem" \
  --exclude 'node_modules' \
  --exclude '.git' \
  /本地项目目录/ \
  root@<YOUR_SERVER_IP>:/root/ai-frontiers/
```

---

## 4. 服务器环境配置

### 4.1 首次登录配置

```bash
# 更新系统
apt update && apt upgrade -y

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 验证时区
date
```

### 4.2 安装 Docker

#### 步骤 1：安装依赖包
```bash
apt install -y ca-certificates curl gnupg lsb-release git vim wget htop
```

#### 步骤 2：添加 Docker GPG 密钥
```bash
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

#### 步骤 3：添加 Docker 仓库
```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### 步骤 4：安装 Docker
```bash
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### 步骤 5：启动 Docker
```bash
systemctl start docker
systemctl enable docker
```

#### 步骤 6：验证安装
```bash
docker --version
docker compose version
```

### 4.3 配置 Docker 镜像加速（国内必须）

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

# 重启 Docker 生效
systemctl daemon-reload
systemctl restart docker
```

### 4.4 配置防火墙

```bash
# 安装 UFW
apt install -y ufw

# 允许必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# 启用防火墙
ufw --force enable

# 查看状态
ufw status
```

### 4.5 创建 Swap（小内存服务器建议）

```bash
# 检查是否有 swap
swapon --show

# 如果没有，创建 2GB swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' >> /etc/fstab
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# 验证
free -h
```

---

## 5. 项目部署

### 5.1 上传项目代码

#### 方式一：本地打包上传

**本地 Mac/Linux 执行：**
```bash
# 打包项目
cd /path/to/ai-frontiers
tar --exclude='node_modules' --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='.env' -czvf /tmp/ai-frontiers.tar.gz .

# 上传到服务器
scp -i ~/.ssh/your_key.pem /tmp/ai-frontiers.tar.gz root@<YOUR_SERVER_IP>:/root/
```

**服务器执行：**
```bash
# 解压项目
cd /root
mkdir -p ai-frontiers
tar -xzvf ai-frontiers.tar.gz -C ai-frontiers
cd /root/ai-frontiers
```

#### 方式二：Git 克隆

```bash
cd /root
git clone https://github.com/yourusername/ai-frontiers.git
cd ai-frontiers
```

### 5.2 配置环境变量

```bash
cd /root/ai-frontiers

# 创建 .env 文件
cat > .env << 'EOF'
# 数据库配置
DATABASE_URL=postgresql://aifrontiers:AiFrontiers2024!@postgres:5432/aifrontiers
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis配置
REDIS_URL=redis://:RedisPass2024!@redis:6379/0

# 环境配置
ENVIRONMENT=production
DEBUG=false

# 安全配置
SECRET_KEY=your_random_secret_key_here

# 前端配置
NEXT_PUBLIC_API_URL=http://<YOUR_SERVER_IP>/api
NEXT_PUBLIC_APP_URL=http://<YOUR_SERVER_IP>

# 爬虫配置
CRAWLER_INTERVAL_MINUTES=15
CRAWLER_MAX_RETRIES=3
CRAWLER_TIMEOUT=30

# 监控配置
ENABLE_METRICS=false
ENABLE_TRACING=false
EOF

# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32) && sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
```

### 5.3 部署命令

```bash
# 进入项目目录
cd /root/ai-frontiers

# 拉取基础镜像
docker compose -f docker-compose.prod.yml pull

# 构建项目镜像
docker compose -f docker-compose.prod.yml build

# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 5.4 验证部署

```bash
# 检查服务状态
docker compose -f docker-compose.prod.yml ps

# 应该看到所有服务状态为 healthy 或 Up
# NAME                   STATUS
# aifrontiers-api        Up (healthy)
# aifrontiers-frontend   Up
# aifrontiers-nginx      Up
# aifrontiers-postgres   Up (healthy)
# aifrontiers-redis      Up (healthy)

# 测试 API
curl http://localhost/health
# 应该返回: {"status":"healthy","version":"0.1.0","environment":"production"}

# 测试前端
curl -I http://localhost:3000
```

### 5.5 配置安全组（必须）

在阿里云控制台配置：

1. 打开阿里云控制台：https://ecs.console.aliyun.com
2. 点击实例ID进入详情
3. 左侧点击 **安全组**
4. 点击安全组ID
5. 点击 **配置规则** → **入方向** → **手动添加**

添加以下规则：

| 授权策略 | 优先级 | 协议类型 | 端口范围 | 授权对象 | 描述 |
|----------|--------|----------|----------|----------|------|
| 允许 | 1 | TCP | 22/22 | 0.0.0.0/0 | SSH |
| 允许 | 1 | TCP | 80/80 | 0.0.0.0/0 | HTTP |
| 允许 | 1 | TCP | 443/443 | 0.0.0.0/0 | HTTPS |

### 5.6 运行爬虫获取数据

```bash
# 进入 API 容器运行爬虫
docker compose -f docker-compose.prod.yml exec api python scripts/fetch_arxiv.py
```

---

## 6. 常见问题与解决方案

### 6.1 SSH 连接问题

#### 问题：Connection refused
```
检查:
1. 安全组是否开放 22 端口
2. 实例是否运行中
3. 密码是否正确

解决:
控制台 → 实例 → 安全组 → 配置规则 → 添加入方向规则
端口: 22, 协议: TCP, 授权对象: 0.0.0.0/0
```

#### 问题：Permission denied (publickey)
```
原因: 密钥文件路径错误或权限不正确

解决:
1. 确认密钥文件存在
   ls -la ~/.ssh/your_key.pem

2. 设置正确权限
   chmod 600 ~/.ssh/your_key.pem

3. 使用正确的密钥路径
   ssh -i ~/.ssh/your_key.pem root@<YOUR_SERVER_IP>
```

### 6.2 网站无法访问

#### 问题：浏览器显示无法访问
```
检查清单:
1. 实例是否运行中
2. 安全组是否开放 80/443 端口
3. 防火墙是否放行
4. Docker 容器是否运行

# 检查安全组
控制台 → 实例 → 安全组 → 配置规则

# 检查防火墙
ufw status

# 检查容器
docker ps

# 检查端口监听
netstat -tlnp | grep 80
```

### 6.3 Docker 构建问题

#### 问题：pip install 超时
```
原因: 国内访问 pypi.org 较慢

解决: 在 Dockerfile 中配置国内镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题：apt-get 超时
```
原因: 国内访问 deb.debian.org 较慢

解决: 在 Dockerfile 中配置阿里云镜像
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources
```

#### 问题：no space left on device
```
原因: Docker 缓存占用磁盘空间

解决:
# 清理 Docker 缓存
docker system prune -a -f --volumes

# 查看磁盘空间
df -h
```

### 6.4 容器启动问题

#### 问题：容器不断重启
```
# 查看容器日志
docker logs aifrontiers-api --tail 50
docker logs aifrontiers-nginx --tail 50
docker logs aifrontiers-frontend --tail 50

# 根据日志内容解决具体问题
```

#### 问题：API 模块找不到
```
# 确保在 Dockerfile 中复制了所有必要的文件
COPY api/ .
COPY scripts/ ./scripts/
```

#### 问题：Nginx SSL 证书错误
```
原因: SSL 证书文件不存在

解决: 使用简化版 nginx 配置（仅 HTTP）
# 在 docker-compose.prod.yml 中使用
- ./deployment/nginx/nginx-simple.conf:/etc/nginx/nginx.conf:ro
```

### 6.5 数据库问题

#### 问题：pgvector 扩展不存在
```
原因: 标准 PostgreSQL 镜像不包含 pgvector

解决:
1. 使用简化版 init-db.sql（不使用 pgvector）
2. 或使用 pgvector/pgvector 镜像（国内可能无法拉取）
```

---

## 7. 日常运维

### 7.1 服务管理命令

```bash
# 查看容器状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f frontend

# 重启服务
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml restart api

# 停止服务
docker compose -f docker-compose.prod.yml down

# 启动服务
docker compose -f docker-compose.prod.yml up -d
```

### 7.2 进入容器

```bash
# 进入 API 容器
docker compose -f docker-compose.prod.yml exec api bash

# 进入数据库容器
docker compose -f docker-compose.prod.yml exec postgres bash

# 进入 Redis 容器
docker compose -f docker-compose.prod.yml exec redis sh
```

### 7.3 数据库操作

```bash
# 连接 PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres psql -U aifrontiers -d aifrontiers

# 备份数据库
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U aifrontiers aifrontiers > backup.sql

# 恢复数据库
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U aifrontiers aifrontiers
```

### 7.4 系统监控

```bash
# CPU/内存监控
htop

# 磁盘空间
df -h

# 内存使用
free -h

# 网络连接
netstat -tlnp

# Docker 资源使用
docker stats
```

### 7.5 日志管理

```bash
# 查看系统日志
journalctl -u docker

# 查看 Nginx 访问日志
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/access.log

# 查看 Nginx 错误日志
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log
```

### 7.6 更新部署

```bash
# 拉取最新代码
cd /root/ai-frontiers
git pull

# 重新构建并部署
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## 附录：快速命令参考

### 一键部署命令

```bash
# 服务器环境配置
apt update && apt upgrade -y
timedatectl set-timezone Asia/Shanghai
apt install -y ca-certificates curl gnupg lsb-release git vim wget htop
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl start docker && systemctl enable docker

# 配置 Docker 镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://docker.anyhub.us.kg",
    "https://dockerhub.icu"
  ]
}
EOF
systemctl daemon-reload && systemctl restart docker

# 配置防火墙
apt install -y ufw
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 部署项目
cd /root/ai-frontiers
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

**文档版本**: 1.0
**创建日期**: 2026-03-28
**服务器 IP**: `<YOUR_SERVER_IP>`
**项目**: AI Frontiers
