# AWS 云服务器部署指南

> AI Frontiers 项目部署到 AWS EC2 的完整流程

---

## 目录

1. [注册 AWS 账号](#1-注册-aws-账号)
2. [启动 EC2 实例](#2-启动-ec2-实例)
3. [连接服务器](#3-连接服务器)
4. [安装 Docker 环境](#4-安装-docker-环境)
5. [部署项目](#5-部署项目)
6. [配置域名和 SSL](#6-配置域名和-ssl)
7. [费用说明](#7-费用说明)
8. [常见问题](#8-常见问题)

---

## 1. 注册 AWS 账号

### 1.1 访问 AWS 官网

```
https://aws.amazon.com
```

### 1.2 创建账户

1. 点击 **"创建 AWS 账户"** 按钮
2. 填写以下信息：
   - 邮箱地址
   - 密码（至少8位，包含大小写字母、数字、特殊字符）
   - AWS 账户名称
3. 点击 **"验证邮箱"**
4. 输入收到的验证码

### 1.3 设置 Root 用户密码

```
- 至少 8 个字符
- 包含大写字母
- 包含小写字母
- 包含数字
- 包含特殊字符 (!@#$%^&* 等)
```

### 1.4 选择账户类型

```
☐ 商业用途
☑ 个人用途  ← 选择这个
```

### 1.5 填写联系信息

```
- 全名
- 电话号码（需要验证）
- 国家/地区
- 地址
- 城市
- 省/自治区
- 邮政编码
```

### 1.6 绑定支付方式

⚠️ **重要**：需要绑定信用卡或借记卡

```
支持的方式：
- Visa
- MasterCard
- American Express
- 银联（部分）
```

### 1.7 验证身份

```
1. 选择验证方式：短信或语音通话
2. 输入手机号码
3. 接收验证码
4. 输入验证码完成验证
```

### 1.8 选择支持计划

```
☐ 开发人员支持 - $29/月
☐ 商业支持 - $100/月
☑ 基本支持 - 免费  ← 选择这个
```

### 1.9 完成注册

```
等待账户激活（通常几分钟到24小时）
收到邮件通知后即可登录
```

---

## 2. 启动 EC2 实例

### 2.1 登录 AWS 控制台

```
https://console.aws.amazon.com
```

### 2.2 进入 EC2 服务

```
方法1: 搜索栏输入 "EC2" → 点击进入
方法2: 服务菜单 → 计算 → EC2
```

### 2.3 启动实例

点击 **"启动实例"** 按钮

### 2.4 配置实例详情

#### 基本信息

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 名称 | `ai-frontiers-server` | 实例名称，便于识别 |

#### 操作系统 (AMI)

```
选择: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
类型: 64位 (x86)

为什么选 Ubuntu?
- 社区支持好
- Docker 兼容性最佳
- 文档丰富
```

#### 实例类型

| 类型 | vCPU | 内存 | 适用场景 | 月费用 |
|------|------|------|----------|--------|
| t2.micro | 1 | 1GB | 测试开发 | 免费(12个月) |
| t3.small | 2 | 2GB | 小型应用 | ~$15 |
| **t3.medium** | 2 | 4GB | **推荐本项目** | ~$30 |
| t3.large | 2 | 8GB | 中型应用 | ~$60 |

#### 密钥对

```
1. 点击 "创建新密钥对"
2. 密钥对名称: ai-frontiers-key
3. 密钥对类型: RSA
4. 私钥文件格式: .pem (Mac/Linux) 或 .ppk (Windows)
5. 点击 "创建密钥对"
6. 自动下载密钥文件 → 妥善保存！
```

⚠️ **警告**：密钥文件只下载一次，丢失无法恢复！

#### 网络设置

```
VPC: 默认
子网: 默认
自动分配公有 IP: 启用

防火墙（安全组）:
☑ 创建安全组
☑ 允许 SSH 流量 - 来源: 任何位置 0.0.0.0/0
☑ 允许 HTTP 流量 - 来源: 任何位置 0.0.0.0/0
☑ 允许 HTTPS 流量 - 来源: 任何位置 0.0.0.0/0
```

#### 配置存储

```
大小: 30 GB
类型: gp3 (通用目的 SSD)
IOPS: 3000 (默认)
吞吐量: 125 MB/s (默认)

注意: 30GB 在免费套餐范围内
```

### 2.5 高级配置（可选）

```yaml
详细信息:
  - 购买选项: 按需
  - IAM 实例配置文件: 无
  - 关闭终止行为: 停止
  - 停止保护: 禁用
  - 终止保护: 禁用

用户数据 (可选):
  #!/bin/bash
  # 自动安装 Docker
  curl -fsSL https://get.docker.com | sh
  usermod -aG docker ubuntu
```

### 2.6 启动实例

1. 检查配置摘要
2. 点击 **"启动实例"**
3. 等待实例启动（约1-2分钟）

---

## 3. 连接服务器

### 3.1 获取实例信息

```
EC2 控制台 → 实例 → 选择实例

记录以下信息:
- 实例 ID: i-xxxxxxxx
- 公有 IPv4 地址: xx.xx.xx.xx
- 公有 IPv4 DNS: ec2-xx-xx-xx-xx.region.compute.amazonaws.com
```

### 3.2 准备密钥文件

#### Mac / Linux

```bash
# 移动密钥文件到安全目录
mkdir -p ~/.ssh
mv ~/Downloads/ai-frontiers-key.pem ~/.ssh/

# 设置正确的权限 (必须!)
chmod 400 ~/.ssh/ai-frontiers-key.pem

# 验证权限
ls -l ~/.ssh/ai-frontiers-key.pem
# 应显示: -r-------- 1 user user ...
```

#### Windows (PowerShell)

```powershell
# 移动密钥文件
mkdir C:\Users\你的用户名\.ssh
move Downloads\ai-frontiers-key.pem C:\Users\你的用户名\.ssh\

# 设置权限 (需要管理员权限)
icacls C:\Users\你的用户名\.ssh\ai-frontiers-key.pem /inheritance:r
icacls C:\Users\你的用户名\.ssh\ai-frontiers-key.pem /grant:r "$($env:USERNAME):R"
```

### 3.3 SSH 连接

#### Mac / Linux

```bash
# 基本连接
ssh -i ~/.ssh/ai-frontiers-key.pem ubuntu@你的公网IP

# 示例
ssh -i ~/.ssh/ai-frontiers-key.pem ubuntu@54.123.45.67

# 首次连接会提示确认指纹，输入 yes
```

#### Windows

```powershell
# 使用 PowerShell 或 Windows Terminal
ssh -i C:\Users\你的用户名\.ssh\ai-frontiers-key.pem ubuntu@你的公网IP
```

#### 使用 SSH 配置文件（推荐）

```bash
# 编辑配置文件
nano ~/.ssh/config

# 添加以下内容
Host aifrontiers
    HostName 你的公网IP
    User ubuntu
    IdentityFile ~/.ssh/ai-frontiers-key.pem

# 保存后可以直接使用
ssh aifrontiers
```

### 3.4 验证连接

```bash
# 连接成功后会看到类似提示
Welcome to Ubuntu 22.04.3 LTS

# 检查系统信息
uname -a
lsb_release -a

# 检查资源
df -h        # 磁盘空间
free -h      # 内存
nproc        # CPU 核心数
```

---

## 4. 安装 Docker 环境

### 4.1 更新系统

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件包
sudo apt upgrade -y

# 安装必要的工具
sudo apt install -y curl wget git vim
```

### 4.2 安装 Docker

```bash
# 使用官方脚本安装（最简单）
curl -fsSL https://get.docker.com | sh

# 将当前用户添加到 docker 组
sudo usermod -aG docker ubuntu

# 验证安装
docker --version
# 输出: Docker version 24.x.x, build xxxxxxx
```

### 4.3 安装 Docker Compose

```bash
# 安装 Docker Compose 插件
sudo apt install -y docker-compose-plugin

# 验证安装
docker compose version
# 输出: Docker Compose version v2.x.x
```

### 4.4 配置 Docker（可选优化）

```bash
# 创建 Docker 配置目录
sudo mkdir -p /etc/docker

# 配置 Docker daemon
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "live-restore": true
}
EOF

# 重启 Docker 服务
sudo systemctl restart docker

# 设置开机自启
sudo systemctl enable docker
```

### 4.5 使组权限生效

```bash
# 重要：登出再登录使 docker 组生效
exit

# 重新连接
ssh aifrontiers

# 验证 docker 命令（不需要 sudo）
docker ps
docker run hello-world
```

---

## 5. 部署项目

### 5.1 上传项目代码

#### 方式一：从 GitHub 克隆（推荐）

```bash
# 安装 Git（如果没有）
sudo apt install -y git

# 克隆项目
git clone https://github.com/yourusername/ai-frontiers.git

# 进入项目目录
cd ai-frontiers
```

#### 方式二：使用 SCP 上传

```bash
# 在本地电脑执行
# 打包项目
tar -czvf ai-frontiers.tar.gz /path/to/ai-frontiers

# 上传到服务器
scp -i ~/.ssh/ai-frontiers-key.pem ai-frontiers.tar.gz ubuntu@你的IP:~

# 在服务器上解压
ssh aifrontiers
tar -xzvf ~/ai-frontiers.tar.gz
cd ai-frontiers
```

#### 方式三：使用 rsync 同步（开发推荐）

```bash
# 在本地电脑执行
rsync -avz -e "ssh -i ~/.ssh/ai-frontiers-key.pem" \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  /path/to/ai-frontiers/ \
  ubuntu@你的IP:~/ai-frontiers/
```

### 5.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

#### 必填配置项

```bash
# 数据库配置
POSTGRES_USER=aifrontiers
POSTGRES_PASSWORD=你的安全密码123!
POSTGRES_DB=aifrontiers

# Redis 配置
REDIS_PASSWORD=你的Redis密码456!

# API Keys（必填）
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# 应用配置
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=你的随机密钥789!

# 域名（如果有）
DOMAIN=yourdomain.com
```

#### 生成随机密钥

```bash
# 生成 SECRET_KEY
openssl rand -hex 32

# 生成密码
openssl rand -base64 24
```

### 5.3 执行部署

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

#### 部署脚本执行内容

```bash
1. ✓ 检查 Docker 环境
2. ✓ 创建必要目录
3. ✓ 拉取 Docker 镜像
4. ✓ 构建项目镜像
5. ✓ 启动所有服务
6. ✓ 等待服务就绪
7. ✓ 执行健康检查
```

### 5.4 验证部署

```bash
# 查看运行中的容器
docker ps

# 应该看到以下容器:
# - aifrontiers-postgres
# - aifrontiers-redis
# - aifrontiers-api
# - aifrontiers-frontend
# - aifrontiers-nginx

# 检查 API 健康状态
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 5.5 运行爬虫获取数据

```bash
# 进入 API 容器
docker compose -f docker-compose.prod.yml exec api bash

# 运行爬虫
python scripts/fetch_arxiv.py

# 查看 Python 输出
# 应该看到: "获取到 XX 篇论文"

# 退出容器
exit
```

### 5.6 访问应用

```
浏览器访问:
- 前端: http://你的公网IP
- API 文档: http://你的公网IP/api/docs
- 健康检查: http://你的公网IP/health
```

---

## 6. 配置域名和 SSL

### 6.1 购买域名

推荐域名注册商：

| 注册商 | 价格 | 特点 |
|--------|------|------|
| Namecheap | $8.88/年 | 便宜，免费隐私保护 |
| Cloudflare | $8.03/年 | 成本价，免费代理 |
| GoDaddy | $11.99/年 | 知名度高 |
| 阿里云 | ¥55/年 | 国内访问快 |

### 6.2 配置 DNS 解析

#### 在域名注册商添加 A 记录

```
类型: A
名称: @
值: 你的AWS公网IP
TTL: 600 (10分钟)

类型: A
名称: www
值: 你的AWS公网IP
TTL: 600
```

#### 验证 DNS 解析

```bash
# 等待几分钟，然后验证
ping yourdomain.com

# 应该返回你的 AWS IP
```

### 6.3 安装 SSL 证书

#### 使用 Certbot (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install -y certbot

# 停止 Nginx（如果正在运行）
docker compose -f docker-compose.prod.yml stop nginx

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 按提示输入:
# - 邮箱地址
# - 同意服务条款
# - 是否接收邮件（可选 N）

# 证书位置
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### 复制证书到项目

```bash
# 创建 SSL 目录
mkdir -p deployment/nginx/ssl

# 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/nginx/ssl/key.pem

# 修改权限
sudo chown -R ubuntu:ubuntu deployment/nginx/ssl
chmod 600 deployment/nginx/ssl/*.pem
```

#### 重启服务

```bash
# 重启所有服务
docker compose -f docker-compose.prod.yml up -d

# 验证 HTTPS
curl https://yourdomain.com/health
```

### 6.4 设置自动续期

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加自动续期任务
sudo crontab -e

# 添加以下行（每天检查两次）
0 0,12 * * * certbot renew --quiet --post-hook "docker compose -f /home/ubuntu/ai-frontiers/docker-compose.prod.yml restart nginx"
```

---

## 7. 费用说明

### 7.1 AWS EC2 定价

| 资源 | 配置 | 月费用 |
|------|------|--------|
| EC2 t3.medium | 2vCPU, 4GB | ~$30.37 |
| EBS gp3 30GB | 30GB SSD | ~$2.40 |
| 数据传输 | 100GB 出站 | ~$8.00 |
| 弹性 IP | 1个 | 免费（绑定实例时） |
| **总计** | - | **~$40.77/月** |

### 7.2 免费套餐（新用户）

```
✓ EC2 t2.micro - 750小时/月 (12个月)
✓ EBS 30GB - (12个月)
✓ 数据传输 - 100GB/月 (12个月)

总价值: ~$170/年
```

### 7.3 节省成本技巧

#### 使用 Reserved Instances

```
预付1年: 节省 ~30-40%
预付3年: 节省 ~50-60%
```

#### 使用 Spot Instances

```
竞价实例: 节省 70-90%
缺点: 可能被中断，适合批处理任务
```

#### 使用 Savings Plans

```
承诺使用量: 节省 20-72%
灵活: 适用于 EC2, Lambda, Fargate
```

### 7.4 设置预算提醒

```bash
# AWS 控制台
# 计费 → 预算 → 创建预算

建议设置:
- 月预算: $50
- 警告阈值: 80% ($40)
- 通知邮箱: your@email.com
```

---

## 8. 常见问题

### 8.1 SSH 连接被拒绝

```bash
# 错误: Connection refused

解决方案:
1. 检查安全组是否开放 22 端口
2. 检查实例是否正在运行
3. 检查密钥文件权限 (chmod 400)
4. 检查密钥是否正确
```

### 8.2 Permission denied (publickey)

```bash
# 错误: Permission denied (publickey)

解决方案:
1. 确认使用正确的用户名 (ubuntu)
2. 确认密钥文件路径正确
3. 重新下载密钥对

ssh -i ~/.ssh/ai-frontiers-key.pem ubuntu@你的IP
```

### 8.3 Docker 命令需要 sudo

```bash
# 问题: docker: permission denied

解决方案:
# 重新添加用户到 docker 组
sudo usermod -aG docker ubuntu

# 登出再登录
exit
ssh aifrontiers
```

### 8.4 端口无法访问

```bash
# 问题: 访问 IP 显示连接超时

解决方案:
1. 检查安全组入站规则
2. 检查容器是否运行 (docker ps)
3. 检查防火墙 (sudo ufw status)

# 添加安全组规则
EC2 → 安全组 → 编辑入站规则
添加: HTTP 80, HTTPS 443
```

### 8.5 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理 Docker
docker system prune -a

# 清理日志
sudo journalctl --vacuum-time=3d

# 扩展 EBS 卷（需要重启）
# AWS 控制台 → 卷 → 修改卷 → 增加大小
```

### 8.6 内存不足

```bash
# 检查内存
free -h

# 添加 Swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 附录：常用命令速查

### 服务器管理

```bash
# 查看系统状态
htop                    # CPU/内存监控
df -h                   # 磁盘空间
free -h                 # 内存使用
uptime                  # 运行时间

# 重启/关机
sudo reboot
sudo shutdown -h now
```

### Docker 命令

```bash
# 查看容器
docker ps               # 运行中的容器
docker ps -a            # 所有容器

# 日志
docker logs 容器名
docker logs -f 容器名   # 实时日志
docker logs --tail 100 容器名

# 进入容器
docker exec -it 容器名 bash

# 重启服务
docker compose restart
docker compose restart api

# 停止/启动
docker compose down
docker compose up -d
```

### 文件传输

```bash
# 上传文件
scp -i ~/.ssh/key.pem file.txt ubuntu@IP:~

# 下载文件
scp -i ~/.ssh/key.pem ubuntu@IP:~/file.txt ./

# 同步目录
rsync -avz -e "ssh -i ~/.ssh/key.pem" ./local/ ubuntu@IP:~/remote/
```

---

## 联系支持

- AWS 文档: https://docs.aws.amazon.com
- AWS 论坛: https://forums.aws.amazon.com
- 技术支持: AWS Support Center

---

**文档版本**: 1.0
**更新日期**: 2026-03-27
**适用项目**: AI Frontiers
