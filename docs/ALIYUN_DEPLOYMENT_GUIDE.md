# 阿里云服务器部署指南

> AI Frontiers 项目部署到阿里云 ECS 的完整流程

---

## 目录

1. [注册阿里云账号](#1-注册阿里云账号)
2. [购买 ECS 云服务器](#2-购买-ecs-云服务器)
3. [连接服务器](#3-连接服务器)
4. [配置服务器环境](#4-配置服务器环境)
5. [部署项目](#5-部署项目)
6. [配置域名和 SSL](#6-配置域名和-ssl)
7. [费用说明](#7-费用说明)
8. [常见问题](#8-常见问题)

---

## 1. 注册阿里云账号

### 1.1 访问阿里云官网

```
https://www.aliyun.com
```

### 1.2 注册账号

1. 点击右上角 **"免费注册"**
2. 选择注册方式：
   - 手机号注册（推荐）
   - 邮箱注册
3. 填写手机号/邮箱
4. 获取并输入验证码
5. 设置密码

```
密码要求:
- 8-20 个字符
- 包含字母和数字
- 区分大小写
```

### 1.3 实名认证（必须）

⚠️ **重要**：购买服务器必须完成实名认证

#### 个人认证

```
1. 登录阿里云控制台
2. 点击右上角头像 → 实名认证
3. 选择 "个人认证"
4. 填写真实姓名和身份证号
5. 选择认证方式:
   - 人脸识别（推荐，即时完成）
   - 阿里云 App 扫码
6. 完成认证
```

#### 企业认证（可选）

```
1. 选择 "企业认证"
2. 填写企业信息:
   - 企业名称
   - 统一社会信用代码
   - 法人姓名
   - 法人身份证号
3. 上传营业执照照片
4. 等待审核（1-3 个工作日）
```

### 1.4 充值账户

```
控制台 → 费用 → 充值

支持方式:
- 支付宝
- 银行卡
- 网银

建议首次充值: ¥100-200
```

---

## 2. 购买 ECS 云服务器

### 2.1 进入购买页面

```
方式1: 控制台 → 云服务器 ECS → 创建实例
方式2: 产品页 → 云服务器 ECS → 立即购买
```

### 2.2 选择付费模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **包年包月** | 预付费，更便宜 | 长期稳定使用（推荐） |
| 按量付费 | 后付费，按小时计费 | 测试、临时使用 |
| 抢占式实例 | 竞价，最便宜 | 可能被回收 |

**推荐**: 包年包月，1年享85折

### 2.3 选择地域和可用区

```
地域选择原则:
1. 就近原则: 选择离用户最近的地域
2. 合规要求: 数据必须存储在国内
3. 价格差异: 不同地域价格略有不同

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
| 香港 | 海外/国际用户 | 中 |

### 2.4 选择实例规格

#### 推荐配置

| 规格 | vCPU | 内存 | 适用场景 | 月费用 |
|------|------|------|----------|--------|
| ecs.t5-c1m2.large | 2 | 4GB | **推荐本项目** | ~¥80 |
| ecs.c6.large | 2 | 4GB | 计算型，性能更好 | ~¥150 |
| ecs.g6.large | 2 | 8GB | 需要更多内存 | ~¥200 |

#### 选择方法

```
1. 点击 "企业级" 或 "入门级"
2. 选择 "计算型" 或 "通用型"
3. 筛选条件:
   - vCPU: 2核
   - 内存: 4GB
4. 选择 ecs.c6.large 或 ecs.t5-c1m2.large
```

### 2.5 选择镜像

```
镜像类型: 公共镜像
操作系统: Ubuntu
版本: Ubuntu 22.04 64位

为什么选 Ubuntu 22.04?
- LTS 长期支持版本
- Docker 兼容性最好
- 社区支持丰富
```

### 2.6 选择存储

```
系统盘:
- 类型: ESSD 云盘（推荐）
- 大小: 40GB（免费）
- 性能: PL0（单盘最高 10000 IOPS）

数据盘（可选）:
- 类型: ESSD 云盘
- 大小: 20-100GB
- 用途: 数据库、日志存储

建议: 初期使用 40GB 系统盘足够
```

### 2.7 选择网络和安全组

#### 网络类型

```
☑ 专有网络 VPC（推荐）

VPC: 默认 VPC
交换机: 默认交换机
公网 IP: 分配
带宽计费: 按固定带宽
带宽: 5 Mbps（足够使用）
```

#### 安全组配置

```
☑ 自动创建安全组
☑ 开放 HTTP(80) 端口
☑ 开放 HTTPS(443) 端口
☑ 开放 SSH(22) 端口

安全组规则:
入方向:
  - 端口 22, 协议 TCP, 源 0.0.0.0/0
  - 端口 80, 协议 TCP, 源 0.0.0.0/0
  - 端口 443, 协议 TCP, 源 0.0.0.0/0
```

### 2.8 设置登录凭证

```
登录方式:
  ☑ 自定义密码（推荐）

用户名: root
密码: 你的安全密码123!
确认密码: 你的安全密码123!

⚠️ 密码要求:
- 8-30 个字符
- 包含大写字母
- 包含小写字母
- 包含数字
- 包含特殊字符 (!@#$%^&* 等)
```

### 2.9 确认订单

```
1. 检查配置信息
2. 勾选 "我已阅读并同意《云服务器 ECS 服务条款》"
3. 点击 "确认订单"
4. 完成支付
```

### 2.10 等待实例创建

```
创建时间: 约 1-3 分钟
状态: 从 "创建中" 变为 "运行中"

记录以下信息:
- 实例 ID: i-xxxxxxxxxxxxxxx
- 公网 IP: xx.xx.xx.xx
- 内网 IP: 172.x.x.x
- 实例名称: 可自定义
```

---

## 3. 连接服务器

### 3.1 获取连接信息

```
控制台 → 云服务器 ECS → 实例列表

找到你的实例，记录:
- 公网 IP 地址: xx.xx.xx.xx
- 实例 ID
- 实例状态: 运行中
```

### 3.2 Windows 连接方式

#### 方式一：使用 Workbench（推荐，无需安装）

```
1. 在实例列表，点击 "远程连接"
2. 选择 "通过 Workbench 远程连接"
3. 输入用户名: root
4. 输入密码: 你设置的密码
5. 点击 "确定"
```

#### 方式二：使用 PowerShell / CMD

```powershell
# 打开 PowerShell 或 CMD
ssh root@你的公网IP

# 首次连接提示，输入 yes
# 输入密码（不显示，直接输入后回车）
```

#### 方式三：使用 PuTTY

```
1. 下载 PuTTY: https://www.putty.org
2. 打开 PuTTY
3. Host Name: 输入公网 IP
4. Port: 22
5. Connection Type: SSH
6. 点击 Open
7. 输入用户名: root
8. 输入密码
```

### 3.3 Mac / Linux 连接方式

```bash
# 打开终端
ssh root@你的公网IP

# 示例
ssh root@47.98.123.45

# 首次连接提示
The authenticity of host '47.98.123.45' can't be established.
ECDSA key fingerprint is SHA256:xxxxx.
Are you sure you want to continue connecting (yes/no)?

# 输入 yes，然后回车

# 输入密码（输入时不显示）
root@47.98.123.45's password:

# 连接成功显示
Welcome to Ubuntu 22.04.3 LTS
```

### 3.4 使用 SSH 密钥登录（更安全）

#### 3.4.1 创建密钥对

```bash
# 在本地电脑生成密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 提示输入文件位置，直接回车使用默认
Enter file to save the key: ~/.ssh/id_rsa

# 提示输入密码，可以直接回车不设置
Enter passphrase:

# 生成两个文件
~/.ssh/id_rsa      # 私钥（保密）
~/.ssh/id_rsa.pub  # 公钥（上传到服务器）
```

#### 3.4.2 上传公钥到服务器

```bash
# 方式1: 使用 ssh-copy-id（Mac/Linux）
ssh-copy-id -i ~/.ssh/id_rsa.pub root@你的公网IP

# 方式2: 手动复制
# 先用密码登录
ssh root@你的公网IP

# 创建 .ssh 目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 在本地复制公钥内容
cat ~/.ssh/id_rsa.pub

# 在服务器添加公钥
nano ~/.ssh/authorized_keys
# 粘贴公钥内容，保存退出

# 设置权限
chmod 600 ~/.ssh/authorized_keys

# 退出
exit
```

#### 3.4.3 使用密钥登录

```bash
# 现在可以直接登录，不需要密码
ssh root@你的公网IP

# 如果使用了自定义密钥文件
ssh -i ~/.ssh/your_key root@你的公网IP
```

### 3.5 配置 SSH 快捷方式

```bash
# 编辑本地 SSH 配置
nano ~/.ssh/config

# 添加以下内容
Host aifrontiers
    HostName 你的公网IP
    User root
    IdentityFile ~/.ssh/id_rsa

# 保存后可以直接使用
ssh aifrontiers
```

---

## 4. 配置服务器环境

### 4.1 首次登录配置

```bash
# 更新系统
apt update && apt upgrade -y

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 验证时区
date
# 应显示: Thu Mar 27 16:00:00 CST 2026
```

### 4.2 创建普通用户（推荐）

```bash
# 创建用户
adduser ubuntu

# 设置密码
# 输入两次密码

# 添加 sudo 权限
usermod -aG sudo ubuntu

# 切换到新用户
su - ubuntu
```

### 4.3 配置防火墙

```bash
# 安装 UFW
apt install -y ufw

# 允许必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# 启用防火墙
ufw enable

# 查看状态
ufw status
```

### 4.4 安装 Docker

```bash
# 更新软件包
apt update

# 安装依赖
apt install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
docker compose version

# 测试运行
docker run hello-world
```

### 4.5 配置 Docker（普通用户）

```bash
# 如果使用普通用户 ubuntu
# 将用户添加到 docker 组
usermod -aG docker ubuntu

# 重新登录生效
exit
ssh aifrontiers
su - ubuntu

# 验证（不需要 sudo）
docker ps
```

### 4.6 安装其他工具

```bash
# 安装常用工具
apt install -y git vim wget curl htop net-tools

# 安装 Node.js（如果需要）
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 安装 Python 3（通常已安装）
apt install -y python3 python3-pip python3-venv
```

### 4.7 配置 Swap（小内存服务器）

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

# 优化 swap 使用
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# 验证
free -h
```

---

## 5. 部署项目

### 5.1 上传项目代码

#### 方式一：Git 克隆（推荐）

```bash
# 安装 Git
apt install -y git

# 克隆项目
git clone https://github.com/yourusername/ai-frontiers.git

# 进入项目目录
cd ai-frontiers
```

#### 方式二：SCP 上传

```bash
# 在本地电脑打包
cd /path/to/ai-frontiers
tar -czvf ai-frontiers.tar.gz .

# 上传到服务器
scp ai-frontiers.tar.gz root@你的IP:/root/

# 在服务器解压
ssh root@你的IP
cd /root
mkdir -p ai-frontiers
tar -xzvf ai-frontiers.tar.gz -C ai-frontiers
cd ai-frontiers
```

#### 方式三：使用 rsync（推荐开发使用）

```bash
# 本地电脑执行
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.env' \
  /path/to/ai-frontiers/ \
  root@你的IP:/root/ai-frontiers/
```

### 5.2 配置环境变量

```bash
# 进入项目目录
cd /root/ai-frontiers

# 复制模板
cp .env.example .env

# 编辑配置
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

### 5.3 修改 Docker 配置（中国镜像加速）

```bash
# 配置 Docker 镜像加速
mkdir -p /etc/docker

# 编辑配置
nano /etc/docker/daemon.json
```

```json
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
```

```bash
# 重启 Docker
systemctl daemon-reload
systemctl restart docker
```

### 5.4 构建和启动服务

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

#### 或手动执行

```bash
# 拉取基础镜像
docker compose -f docker-compose.prod.yml pull

# 构建项目镜像
docker compose -f docker-compose.prod.yml build

# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 查看状态
docker compose -f docker-compose.prod.yml ps
```

### 5.5 检查服务状态

```bash
# 查看运行的容器
docker ps

# 应该看到:
# - aifrontiers-postgres
# - aifrontiers-redis
# - aifrontiers-api
# - aifrontiers-frontend
# - aifrontiers-nginx

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f api
```

### 5.6 健康检查

```bash
# 检查 API
curl http://localhost:8000/health

# 预期输出:
# {"status":"healthy","version":"0.1.0","environment":"production"}

# 检查前端
curl -I http://localhost:3000

# 检查 Nginx
curl -I http://localhost
```

### 5.7 运行爬虫获取数据

```bash
# 进入 API 容器
docker compose -f docker-compose.prod.yml exec api bash

# 运行爬虫
python scripts/fetch_arxiv.py

# 查看输出
# 应该显示: "获取到 XX 篇论文"

# 退出容器
exit
```

### 5.8 访问应用

```
浏览器访问:
- 前端: http://你的公网IP
- API 文档: http://你的公网IP/api/docs
- 健康检查: http://你的公网IP/health
```

---

## 6. 配置域名和 SSL

### 6.1 购买域名

#### 阿里云域名购买

```
1. 访问 https://wanwang.aliyun.com
2. 搜索想要的域名
3. 选择后缀 (.com, .cn 等)
4. 加入购物车
5. 购买（需实名认证）

价格参考:
- .com: ¥55/年
- .cn: ¥29/年
- .net: ¥69/年
```

### 6.2 域名备案（必须）

⚠️ **重要**: 使用国内服务器必须进行 ICP 备案

#### 备案流程

```
1. 控制台 → 搜索 "ICP备案"
2. 点击 "开始备案"
3. 填写主体信息:
   - 个人/企业信息
   - 证件信息
   - 联系方式
4. 填写网站信息:
   - 域名
   - 网站名称
   - 网站内容
5. 上传资料:
   - 身份证照片
   - 手持身份证照片
   - 域名证书
6. 提交审核
7. 等待阿里云初审（1-2天）
8. 等待管局审核（5-20天）
9. 备案成功
```

#### 备案注意事项

```
- 网站名称不能用 "博客"、"论坛" 等词汇
- 需要承诺书签字
- 备案期间网站不能访问
- 备案号需放在网站底部
```

### 6.3 配置域名解析

```
1. 控制台 → 域名 → 解析设置
2. 添加记录:

类型: A
主机记录: @
解析线路: 默认
记录值: 你的公网IP
TTL: 10分钟

类型: A
主机记录: www
解析线路: 默认
记录值: 你的公网IP
TTL: 10分钟

3. 保存
```

#### 验证解析

```bash
# 等待 10 分钟后验证
ping yourdomain.com

# 应该返回你的公网 IP
```

### 6.4 申请免费 SSL 证书

#### 阿里云免费证书

```
1. 控制台 → 搜索 "SSL证书"
2. 点击 "购买证书"
3. 选择:
   - 品牌: Digicert
   - 类型: DV 单域名
   - 规格: 免费版
4. 购买（0元）
5. 申请证书:
   - 填写域名
   - 选择验证方式: DNS 验证
   - 提交申请
6. 按提示添加 DNS 记录验证
7. 等待签发（几分钟到几小时）
```

#### 下载证书

```
1. 证书签发后，点击 "下载"
2. 选择 "Nginx" 格式
3. 下载得到:
   - yourdomain.com.pem  (证书文件)
   - yourdomain.com.key  (私钥文件)
```

### 6.5 配置 Nginx SSL

```bash
# 上传证书到服务器
# 在本地电脑执行
scp yourdomain.com.pem root@你的IP:/root/ai-frontiers/deployment/nginx/ssl/cert.pem
scp yourdomain.com.key root@你的IP:/root/ai-frontiers/deployment/nginx/ssl/key.pem

# 在服务器设置权限
ssh root@你的IP
cd /root/ai-frontiers
chmod 600 deployment/nginx/ssl/*.pem
```

### 6.6 重启服务

```bash
# 重启 Nginx
docker compose -f docker-compose.prod.yml restart nginx

# 或重启所有服务
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### 6.7 验证 HTTPS

```bash
# 测试 HTTPS
curl https://yourdomain.com/health

# 浏览器访问
https://yourdomain.com

# 应该看到小绿锁图标
```

---

## 7. 费用说明

### 7.1 阿里云 ECS 定价

#### 包年包月价格

| 配置 | vCPU | 内存 | 带宽 | 月费用 | 年费用 |
|------|------|------|------|--------|--------|
| ecs.t5-c1m2.large | 2 | 4GB | 5M | ~¥80 | ~¥800 |
| ecs.c6.large | 2 | 4GB | 5M | ~¥150 | ~¥1500 |
| ecs.g6.large | 2 | 8GB | 5M | ~¥200 | ~¥2000 |

#### 按量付费价格

| 配置 | 小时费用 | 月费用（730小时） |
|------|----------|-------------------|
| ecs.t5-c1m2.large | ~¥0.15 | ~¥110 |
| ecs.c6.large | ~¥0.25 | ~¥183 |

### 7.2 新用户优惠

```
新用户专享:
- ecs.t5-c1m2.large (2核4G): ¥99/年
- ecs.c6.large (2核4G): ¥199/年
- 限购 1-3 台
- 限首购
```

### 7.3 其他费用

| 服务 | 费用 |
|------|------|
| 域名 .com | ¥55/年 |
| 域名备案 | 免费 |
| SSL 证书 | 免费 |
| 数据盘 20GB | ~¥6/月 |
| 快照备份 | ~¥0.12/GB/月 |

### 7.4 总费用预估

```
最小配置（新用户优惠）:
- ECS: ¥99/年
- 域名: ¥55/年
- 总计: ¥154/年（约 ¥13/月）

标准配置:
- ECS: ¥800/年
- 域名: ¥55/年
- 总计: ¥855/年（约 ¥71/月）
```

---

## 8. 常见问题

### 8.1 SSH 连接被拒绝

```bash
# 问题: Connection refused

检查:
1. 安全组是否开放 22 端口
2. 实例是否运行中
3. 密码是否正确

解决:
控制台 → 实例 → 安全组 → 配置规则 → 添加入方向规则
端口: 22
协议: TCP
授权对象: 0.0.0.0/0
```

### 8.2 网站无法访问

```bash
# 问题: 浏览器访问显示无法访问

检查清单:
1. 实例是否运行中
2. 安全组是否开放 80/443 端口
3. 防火墙是否放行
4. Docker 容器是否运行
5. 域名是否备案（国内必须）

# 检查安全组
控制台 → 实例 → 安全组 → 配置规则

# 检查防火墙
ufw status

# 检查容器
docker ps
```

### 8.3 域名无法访问

```bash
# 问题: 域名无法访问，IP可以

检查:
1. 域名解析是否正确
2. 域名是否已备案
3. 备案是否已生效

# 验证解析
ping yourdomain.com

# 备案状态
控制台 → ICP备案 → 查看状态
```

### 8.4 Docker 拉取镜像慢

```bash
# 问题: 拉取镜像超时

解决: 配置国内镜像加速
nano /etc/docker/daemon.json

{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://docker.anyhub.us.kg"
  ]
}

systemctl restart docker
```

### 8.5 磁盘空间不足

```bash
# 检查磁盘
df -h

# 清理 Docker
docker system prune -a

# 清理日志
journalctl --vacuum-time=3d

# 扩容磁盘
控制台 → 实例 → 磁盘 → 扩容
```

### 8.6 内存不足

```bash
# 检查内存
free -h

# 添加 Swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 附录：常用命令速查

### 服务管理

```bash
# 查看容器状态
docker ps
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f api

# 重启服务
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml restart api

# 停止服务
docker compose -f docker-compose.prod.yml down

# 启动服务
docker compose -f docker-compose.prod.yml up -d
```

### 系统监控

```bash
# CPU/内存监控
htop

# 磁盘空间
df -h

# 内存使用
free -h

# 网络连接
netstat -tlnp

# 系统负载
uptime
```

### 文件操作

```bash
# 上传文件
scp file.txt root@IP:/root/

# 下载文件
scp root@IP:/root/file.txt ./

# 同步目录
rsync -avz ./local/ root@IP:/root/remote/
```

---

## 联系支持

- 阿里云文档: https://help.aliyun.com
- 工单系统: 控制台 → 工单 → 提交工单
- 客服电话: 95187

---

**文档版本**: 1.0
**更新日期**: 2026-03-27
**适用项目**: AI Frontiers
