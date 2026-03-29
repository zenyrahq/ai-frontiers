# 发布流程指南

> **版本**: 1.0
> **更新日期**: 2026-03-29

---

## 📋 发布流程总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Release Process                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│  │ 1.代码   │──▶│ 2.测试   │──▶│ 3.检查   │──▶│ 4.发布   │──▶│ 5.验证   │      │
│  │ 合并    │   │ 通过    │     清单   │   │ 标签    │   │ 监控    │      │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 代码合并

### 前置条件

- [ ] PR 已通过 Code Review
- [ ] CI 检查全部通过
- [ ] 分支已与 main 同步

### 合并步骤

```bash
# 1. 确保在 main 分支
git checkout main
git pull origin main

# 2. 合并 PR (通过 GitHub UI 或命令行)
gh pr merge <PR_NUMBER> --squash --delete-branch

# 3. 拉取最新代码
git pull origin main
```

---

## 2️⃣ 测试验证

### 本地测试

```bash
# 运行后端测试
cd api
pytest tests/ -v

# 构建前端
cd ../frontend
npm run build
npm run lint
```

### Staging 测试

```bash
# 部署到 staging
docker compose -f docker-compose.staging.yml up -d --build

# 运行集成测试
./scripts/run_integration_tests.sh staging
```

---

## 3️⃣ 发布检查清单

### 运行检查脚本

```bash
./scripts/checklist.sh
```

### 手动检查项

| 检查项 | 说明 |
|--------|------|
| 代码Review | 至少1人Approve |
| 测试覆盖 | 核心功能有测试 |
| 文档更新 | API/架构文档已更新 |
| 变更日志 | CHANGELOG.md已更新 |
| 敏感数据 | 无密钥/密码泄露 |
| 向后兼容 | 无破坏性变更（或有迁移方案） |

---

## 4️⃣ 创建发布

### 自动发布（推荐）

```bash
# Patch 版本 (v1.0.0 -> v1.0.1)
./scripts/release.sh patch "修复搜索bug"

# Minor 版本 (v1.0.0 -> v1.1.0)
./scripts/release.sh minor "添加Redis缓存"

# Major 版本 (v1.0.0 -> v2.0.0)
./scripts/release.sh major "架构重构"
```

### 手动发布

```bash
# 1. 创建标签
git tag -a v1.0.1 -m "Release v1.0.1: 修复搜索bug"

# 2. 推送标签
git push origin v1.0.1

# 3. GitHub 自动构建并部署
```

---

## 5️⃣ 部署验证

### 自动部署

CI/CD 会在标签推送后自动部署到生产环境。

### 手动部署

```bash
# SSH 到服务器
ssh root@<SERVER_IP>

# 拉取最新代码
cd /root/ai-frontiers
git pull origin main

# 重新构建并部署
docker compose -f docker-compose.prod.yml up -d --build

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 前端访问检查
curl http://localhost:3000

# 数据库连接检查
docker compose exec postgres pg_isready
```

---

## 🚨 回滚方案

### 快速回滚

```bash
# 查看最近标签
git tag -l | tail -5

# 回滚到上一版本
git checkout <PREVIOUS_TAG>
docker compose -f docker-compose.prod.yml up -d --build
```

### 数据库回滚

```bash
# 如果有数据库迁移
cd api
alembic downgrade -1
```

---

## 📊 发布后监控

### 监控指标

| 指标 | 检查频率 | 告警阈值 |
|------|----------|----------|
| API可用性 | 1分钟 | <99% |
| 响应时间 | 1分钟 | >500ms |
| 错误率 | 1分钟 | >1% |
| 磁盘空间 | 5分钟 | >80% |

### 查看日志

```bash
# 实时日志
docker compose logs -f api

# 最近错误
docker compose logs api 2>&1 | grep -i error | tail -20
```

---

## 📝 发布通知模板

### 发布成功

```markdown
## 🚀 Release v1.0.1

**发布时间**: 2026-03-29
**发布类型**: Patch

### 变更内容
- 修复搜索接口500错误
- 优化首页加载速度

### 部署状态
✅ 生产环境已部署
✅ 健康检查通过
✅ 监控正常

### 相关Issue
- #123 修复搜索bug
```

### 发布失败

```markdown
## ❌ Release v1.0.1 Failed

**发布时间**: 2026-03-29
**失败原因**: [描述失败原因]

### 当前状态
- 生产环境: 回滚到 v1.0.0
- 影响范围: [描述影响]

### 后续计划
- [ ] 修复问题
- [ ] 重新测试
- [ ] 重新发布
```

---

## 🔧 常用命令速查

```bash
# 查看当前版本
git describe --tags

# 查看发布历史
git tag -l | sort -V

# 查看某版本变更
git log v1.0.0..v1.0.1 --oneline

# 对比版本差异
git diff v1.0.0 v1.0.1

# 删除远程标签（慎用）
git push --delete origin v1.0.1
```

---

**文档版本**: 1.0
**最后更新**: 2026-03-29
