# AI Frontiers - AI前沿信息收集平台

> 一个生产级的AI前沿信息收集、处理和分发平台

## 🎯 项目目标

构建一个能够自动收集、处理、推荐全球AI前沿信息的平台，为用户提供最新、最全面的AI领域动态。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                      │
│  Web App (Next.js) │ Mobile Web │ Admin Dashboard       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    API网关层 (Gateway)                    │
│  Nginx/Kong │ 认证鉴权 │ 限流熔断 │ 负载均衡             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   应用服务层 (Services)                   │
│  内容服务 │ 推荐服务 │ 搜索服务 │ 用户服务 │ API服务    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  数据处理层 (Processing)                  │
│  采集服务 │ NLP处理 │ 翻译服务 │ 知识图谱构建            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据存储层 (Storage)                    │
│  PostgreSQL │ Redis │ Elasticsearch │ Neo4j            │
└─────────────────────────────────────────────────────────┘
```

## 📦 项目结构

```
ai-frontiers/
├── crawler/          # 爬虫服务
│   ├── spiders/      # 爬虫模块
│   ├── scheduler.py  # 调度器
│   └── main.py       # 主入口
├── api/              # 后端API服务
│   ├── routes/       # 路由
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── main.py       # FastAPI主入口
├── processing/       # 数据处理服务
│   ├── nlp/          # NLP处理
│   ├── translation/  # 翻译服务
│   └── embedding/    # 向量化
├── frontend/         # 前端应用
│   ├── app/          # Next.js App Router
│   ├── components/   # React组件
│   └── lib/          # 工具库
├── deployment/       # 部署配置
│   ├── docker/       # Docker配置
│   ├── k8s/          # Kubernetes配置
│   └── nginx/        # Nginx配置
└── docs/             # 文档
    ├── api.md        # API文档
    ├── architecture.md # 架构设计
    └── deployment.md # 部署指南
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 本地开发环境搭建

1. **克隆项目**

```bash
git clone https://github.com/yourusername/ai-frontiers.git
cd ai-frontiers
```

2. **启动基础设施服务**

```bash
docker-compose up -d postgres redis elasticsearch
```

3. **安装Python依赖**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置
```

5. **运行数据库迁移**

```bash
cd api
alembic upgrade head
```

6. **启动后端服务**

```bash
cd api
uvicorn main:app --reload
```

7. **启动前端服务**

```bash
cd frontend
npm install
npm run dev
```

### 访问服务

- 前端: http://localhost:3000
- API文档: http://localhost:8000/docs
- Grafana: http://localhost:3001

## 🔧 配置说明

### 环境变量

```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/aifrontiers

# Redis
REDIS_URL=redis://localhost:6379

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# AI API Keys
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# 其他配置
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📊 功能特性

- ✅ **智能采集**: 支持20+信息源，自动去重和清洗
- ✅ **多语言支持**: 中英日等多语言内容自动翻译
- ✅ **智能推荐**: 基于用户行为的混合推荐算法
- ✅ **知识图谱**: 构建AI领域知识图谱，关联分析
- ✅ **API开放平台**: 提供RESTful API供第三方调用
- ✅ **实时监控**: 完善的监控告警体系

## 📈 开发路线

### Phase 1: MVP (Week 1-4)

- [x] 项目初始化
- [x] 数据库设计（PostgreSQL + pgvector）
- [x] 基础API框架（FastAPI）
- [x] arXiv爬虫服务
- [x] NLP处理流程（Claude API + 向量嵌入）
- [x] 智能搜索服务（向量 + 全文 + 混合）
- [ ] 基础前端页面

### Phase 2: 核心功能 (Week 5-8)

- [ ] 推荐系统
- [ ] 多语言翻译
- [ ] API开放平台
- [ ] 知识图谱

### Phase 3: 优化上线 (Week 9-12)

- [ ] 性能优化
- [ ] 监控告警
- [ ] 部署上线
- [ ] 用户测试

### 当前进度

```
✅ 基础设施 → ✅ arXiv爬虫 → ✅ NLP处理 → ✅ 搜索API → ✅ 前端界面
```

**已完成的模块**:
- ✅ PostgreSQL 18.3 + pgvector 0.8.2
- ✅ Redis 8.6.2
- ✅ FastAPI 后端框架
- ✅ arXiv 论文爬虫
- ✅ Claude API 内容分析
- ✅ Sentence Transformers 向量嵌入
- ✅ 智能搜索服务（8个API端点）
- ✅ Next.js 14 前端界面（首页、搜索页、详情页）

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详细贡献指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页: https://github.com/yourusername/ai-frontiers
- 问题反馈: https://github.com/yourusername/ai-frontiers/issues
- 邮箱: your.email@example.com

## 🙏 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Elasticsearch](https://www.elastic.co/)

---

**Made with ❤️ by AI Frontiers Team**
