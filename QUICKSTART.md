# AI Frontiers 项目 - 快速开始指南

## 🎉 项目已完成配置！

你的AI前沿信息收集平台基础架构已经完全配置好并测试通过！

---

## ✅ 当前状态

### 已安装服务
- ✅ **PostgreSQL 18.3** - 主数据库
- ✅ **pgvector 0.8.2** - 向量搜索扩展
- ✅ **Redis 8.6.2** - 缓存和消息队列
- ✅ **FastAPI 0.128.8** - API框架
- ✅ **Python 3.9.6** - 运行环境

### 已完成配置
- ✅ 数据库Schema设计和迁移
- ✅ 6个核心数据表
- ✅ API基础框架
- ✅ 完整的中文文档

---

## 🚀 快速启动

### 方法1：手动启动（推荐）

```bash
# 1. 启动数据库服务
brew services start postgresql@18
brew services start redis

# 2. 激活Python虚拟环境
source venv/bin/activate

# 3. 启动API服务
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法2：一键启动

```bash
# 如果你在项目根目录
./start.sh
```

---

## 📍 访问地址

启动后，你可以访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| API根路径 | http://localhost:8000/ | API欢迎页面 |
| API文档 | http://localhost:8000/docs | Swagger交互式文档 |
| ReDoc文档 | http://localhost:8000/redoc | ReDoc格式文档 |
| 健康检查 | http://localhost:8000/health | 服务健康状态 |

---

## 📊 API测试

### 测试根路径
```bash
curl http://localhost:8000/
```

预期响应：
```json
{
  "message": "Welcome to AI Frontiers API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### 测试健康检查
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### 测试内容列表（需要认证）
```bash
curl http://localhost:8000/api/v1/contents
```

---

## 🗂️ 项目结构

```
ai-frontiers/
├── api/                    # FastAPI后端
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── routes/            # API路由
│   ├── services/          # 业务逻辑
│   ├── alembic/           # 数据库迁移
│   └── main.py            # 应用入口
├── crawler/               # 爬虫服务（待开发）
├── frontend/              # 前端应用（待开发）
├── processing/            # 数据处理（待开发）
├── docs/                  # 完整文档
├── deployment/            # 部署配置
├── venv/                  # Python虚拟环境
├── .env                   # 环境变量
├── requirements.txt       # Python依赖
└── docker-compose.yml     # Docker配置
```

---

## 📚 文档列表

### 项目文档
- [README.md](../README.md) - 项目说明
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 贡献指南
- [CHANGELOG.md](../CHANGELOG.md) - 更新日志

### 技术文档
- [docs/PROJECT.md](PROJECT.md) - 项目管理
- [docs/architecture.md](architecture.md) - 系统架构
- [docs/api.md](api.md) - API文档
- [docs/TEST_RESULTS.md](TEST_RESULTS.md) - 测试结果
- [docs/INFRASTRUCTURE_TEST_REPORT.md](INFRASTRUCTURE_TEST_REPORT.md) - 基础架构测试报告

---

## 🛠️ 开发指南

### 下一步开发建议

#### 优先级1：核心功能
1. **arXiv爬虫** - 实现论文自动采集
2. **NLP处理** - 内容摘要和分类
3. **搜索功能** - 全文和向量搜索
4. **基础前端** - 内容展示界面

#### 优先级2：增强功能
5. **用户认证** - JWT认证系统
6. **推荐系统** - 个性化推荐
7. **多语言** - 翻译服务
8. **监控告警** - 系统监控

### 开发命令

```bash
# 运行数据库迁移
cd api
alembic upgrade head

# 创建新迁移
alembic revision --autogenerate -m "描述"

# 查看API日志
tail -f logs/api.log

# 运行测试
pytest

# 代码格式化
black .

# 代码检查
flake8 .
```

---

## 🔧 常见问题

### Q1: 如何重置数据库？
```bash
# 删除所有表并重新迁移
cd api
alembic downgrade base
alembic upgrade head
```

### Q2: 如何添加新的API端点？
1. 在 `api/routes/` 创建新路由文件
2. 在 `api/main.py` 注册路由
3. 在 `api/services/` 实现业务逻辑

### Q3: 如何查看数据库数据？
```bash
# 使用psql
/opt/homebrew/opt/postgresql@18/bin/psql -d aifrontiers

# 查看表
\dt

# 查询数据
SELECT * FROM contents LIMIT 10;
```

### Q4: 如何停止所有服务？
```bash
# 停止API
pkill -f "uvicorn main:app"

# 停止数据库（可选）
brew services stop postgresql@18
brew services stop redis
```

---

## 📈 性能优化建议

1. **数据库优化**
   - 添加适当的索引
   - 使用连接池
   - 定期VACUUM

2. **API优化**
   - 使用异步操作
   - 添加缓存层
   - 实现分页查询

3. **缓存策略**
   - Redis缓存热点数据
   - 设置合理的TTL
   - 缓存预热

---

## 🎯 MVP目标

### 3个月目标
- [ ] 1,000用户注册
- [ ] DAU 200+
- [ ] 5,000条内容收录
- [ ] API可用性 99%+

### 成功指标
- ✅ 基础架构完成
- ✅ 文档完整
- ⏳ 核心功能开发
- ⏳ 用户测试

---

## 💡 提示

1. **开发时保持API运行** - 这样可以实时测试端点
2. **定期提交代码** - 使用Git进行版本控制
3. **查看API文档** - http://localhost:8000/docs
4. **监控日志** - 关注错误和性能问题

---

## 📞 获取帮助

- **查看文档**: `docs/` 目录
- **API文档**: http://localhost:8000/docs
- **问题反馈**: 创建GitHub Issue

---

**祝你开发顺利！🚀**

现在你可以开始开发核心功能了！建议从arXiv爬虫开始。
