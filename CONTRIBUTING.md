# 贡献指南

感谢你对 AI Frontiers 项目感兴趣！我们欢迎所有形式的贡献。

## 🤝 贡献方式

### 1. 报告问题

发现Bug或有新功能想法：

1. 先在 [Issues](https://github.com/yourusername/ai-frontiers/issues) 查看是否已有相同问题
2. 创建新Issue，包含以下信息：
   - 问题详细描述
   - 复现步骤（Bug需提供）
   - 期望行为
   - 实际行为
   - 环境信息（操作系统、Python版本等）

### 2. 代码贡献

#### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/ai-frontiers.git
cd ai-frontiers

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

#### 分支策略

- `main`: 生产环境代码
- `develop`: 开发中的代码
- `feature/*`: 新功能开发
- `bugfix/*`: Bug修复
- `hotfix/*`: 紧急生产修复

#### 提交消息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型说明**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（不是新功能也不是修复Bug）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**示例**:
```
feat(crawler): 添加arXiv爬虫

实现了从arXiv自动采集AI论文的功能：
- 支持定时调度
- 自动去重
- 错误处理

Closes #123
```

### 3. Pull Request流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **编写代码**
   - 遵循代码规范
   - 添加测试用例
   - 更新相关文档

3. **代码质量检查**
   ```bash
   # 代码格式化
   black .

   # 代码检查
   flake8 .

   # 类型检查
   mypy .

   # 运行测试
   pytest
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加某个新功能"
   ```

5. **推送代码**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **创建Pull Request**
   - 在GitHub上创建PR
   - 填写PR模板
   - 等待代码审查

### 4. 代码审查

所有PR需要至少1人审查通过：

- 提供建设性的反馈
- 检查代码质量、可维护性、性能
- 确保测试覆盖充分

## 📏 编码规范

### Python

- 遵循 **PEP 8** 规范
- 使用 **Black** 格式化代码
- 添加 **类型注解**
- 编写 **文档字符串**（英文）

```python
def calculate_score(content: str, weights: dict[str, float]) -> float:
    """
    Calculate importance score for content.

    Args:
        content: Text to analyze
        weights: Weight for each factor

    Returns:
        Calculated score (0.0-1.0)

    Raises:
        ValueError: If content is empty
    """
    if not content:
        raise ValueError("Content cannot be empty")

    # Scoring logic
    score = 0.0
    # ...
    return score
```

### JavaScript/TypeScript

- 使用 **ESLint** 和 **Prettier**
- 优先使用 **函数式组件**
- 充分利用 **TypeScript** 类型系统

### 文档

- 使用中文编写
- Markdown格式
- 包含代码示例

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_crawler.py -v
```

### 测试指南

- **单元测试**: 测试单个函数或类
- **集成测试**: 测试多个组件协作
- **E2E测试**: 端到端场景测试

```python
def test_content_processor():
    """Test content processor functionality"""
    processor = ContentProcessor()
    result = processor.process("sample content")

    assert result is not None
    assert len(result.summary) > 0
    assert result.embedding is not None
```

## 📚 文档

### API文档

- 使用FastAPI自动生成的文档
- 为所有端点添加说明
- 包含请求/响应示例

### 架构文档

- 添加新组件时更新 `docs/architecture.md`
- 包含时序图或类图
- 说明依赖关系

## 🚀 发布流程

1. 更新版本号（语义化版本）
2. 更新 `CHANGELOG.md`
3. 创建发布分支
4. 进行最终测试
5. 创建标签
6. 部署上线

## 💬 沟通渠道

- **GitHub Issues**: Bug报告、功能请求
- **Pull Requests**: 代码审查、讨论
- **Discussions**: 一般性问题、想法分享

## 📜 行为准则

- 尊重所有贡献者
- 提供建设性反馈
- 保持开放和包容的态度
- 专注于对项目最有利的事情

## ❓ 常见问题

### Q: 如何开始第一次贡献？

A: 查看 Issues 中标记为 `good first issue` 的问题，这些通常比较简单。

### Q: 代码风格要求是什么？

A: Python遵循PEP 8，使用Black格式化。JavaScript使用ESLint和Prettier。

### Q: 需要写测试吗？

A: 是的，所有新功能都需要有对应的测试用例。

### Q: 如何联系维护者？

A: 可以通过GitHub Issues或Discussions联系。

---

**期待你的贡献！** 🎉
