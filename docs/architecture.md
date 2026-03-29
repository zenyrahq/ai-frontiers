# 系统架构设计

## 📐 架构概览

AI Frontiers采用可扩展、高可用的微服务架构设计。

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    展示层 (Presentation)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Web App    │  │  Mobile Web  │  │    Admin     │ │
│  │  (Next.js)   │  │              │  │  Dashboard   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                      网关层 (Gateway)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │   Nginx (反向代理 + 负载均衡)                      │   │
│  │   - SSL终止                                       │   │
│  │   - 限流                                          │   │
│  │   - 请求路由                                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     服务层 (Service)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │   API    │  │Recommend │  │  Search  │  │  User    ││
│  │ Service  │  │ Service  │  │ Service  │  │ Service  ││
│  │(FastAPI) │  │          │  │          │  │          ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   处理层 (Processing)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Crawler  │  │   NLP    │  │Translation│  │ Knowledge││
│  │ Service  │  │Processor │  │ Service  │  │  Graph   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据层 (Data)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │PostgreSQL│  │  Redis   │  │Elastic   │  │  Neo4j   ││
│  │  (RDB)   │  │ (Cache)  │  │ Search   │  │ (Graph)  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 服务详细设计

### 1. 爬虫服务 (Crawler Service)

**职责**:
- 从多个信息源采集数据
- 去重处理
- 数据清洗
- 任务调度

**技术栈**:
- Python 3.11
- Scrapy
- APScheduler
- Redis (队列)

**核心组件**:

```python
class CrawlerService:
    """
    爬虫服务
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.redis_queue = RedisQueue()
        self.deduplicator = URLDeduplicator()

    async def crawl_source(self, source: SourceConfig):
        """
        爬取指定源

        Args:
            source: 源配置

        Returns:
            采集到的内容列表
        """
        # 实现细节
        pass
```

**调度策略**:
- 重要源: 5分钟间隔
- 标准源: 15分钟间隔
- 低优先级源: 1小时间隔

---

### 2. NLP处理服务 (NLP Processing Service)

**职责**:
- 文本摘要
- 实体提取
- 关键词提取
- 情感分析

**技术栈**:
- Python 3.11
- Claude API (Anthropic)
- Sentence Transformers
- spaCy

**处理流程**:

```
原始内容
    ↓
[文本清洗] → 去除HTML标签、噪声
    ↓
[摘要生成] → Claude API生成200字摘要
    ↓
[实体提取] → 提取模型名、公司名、人名
    ↓
[向量化] → 生成384维向量
    ↓
[分类] → 类别分类（论文、新闻、博客等）
    ↓
处理后内容
```

**API设计**:

```python
class NLPProcessor:
    """
    NLP处理服务
    """

    async def process_content(self, content: str) -> ProcessedContent:
        """
        处理内容

        Args:
            content: 原始文本

        Returns:
            处理后内容（摘要、实体、向量）
        """
        cleaned = await self.clean(content)
        summary = await self.summarize(cleaned)
        entities = await self.extract_entities(cleaned)
        embedding = self.generate_embedding(cleaned)

        return ProcessedContent(
            original=content,
            cleaned=cleaned,
            summary=summary,
            entities=entities,
            embedding=embedding
        )
```

---

### 3. 推荐服务 (Recommendation Service)

**职责**:
- 个性化推荐
- 相似内容推荐
- 热门内容推荐

**推荐算法**:

#### 3.1 协同过滤 (Collaborative Filtering)

```python
def collaborative_filter(user_id: int, k: int = 20) -> List[Content]:
    """
    基于用户的协同过滤

    Args:
        user_id: 用户ID
        k: 推荐数量

    Returns:
        推荐内容列表
    """
    # 1. 找到相似用户
    similar_users = find_similar_users(user_id)

    # 2. 收集相似用户喜欢的内容
    candidate_items = get_items_liked_by_users(similar_users)

    # 3. 计算分数
    scored_items = calculate_scores(candidate_items, similar_users)

    # 4. 返回Top-K
    return scored_items[:k]
```

#### 3.2 基于内容的推荐 (Content-Based Filtering)

```python
def content_based_filter(user_id: int, k: int = 20) -> List[Content]:
    """
    基于内容的推荐

    Args:
        user_id: 用户ID
        k: 推荐数量

    Returns:
        推荐内容列表
    """
    # 1. 获取用户向量
    user_embedding = get_user_embedding(user_id)

    # 2. 向量相似度搜索（Elasticsearch）
    similar_contents = es.search(
        index="contents",
        body={
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding')",
                        "params": {"query_vector": user_embedding}
                    }
                }
            },
            "size": k
        }
    )

    return similar_contents
```

#### 3.3 混合推荐

```python
def hybrid_recommend(user_id: int, k: int = 20) -> List[Content]:
    """
    混合推荐（协同过滤 + 基于内容）

    Args:
        user_id: 用户ID
        k: 推荐数量

    Returns:
        推荐内容列表
    """
    # 各方法推荐
    cf_items = collaborative_filter(user_id, k=50)
    cb_items = content_based_filter(user_id, k=50)
    hot_items = get_hot_items(k=20)

    # 加权合并
    merged = merge_with_weights(
        cf_items,    # 权重: 0.3
        cb_items,    # 权重: 0.5
        hot_items    # 权重: 0.2
    )

    return merged[:k]
```

---

### 4. 搜索服务 (Search Service)

**职责**:
- 全文搜索
- 语义搜索
- 分面搜索

**技术栈**:
- Elasticsearch 8
- KNN搜索（向量搜索）

**索引设计**:

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "summary": {
        "type": "text",
        "analyzer": "standard"
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "source": {
        "type": "keyword"
      },
      "published_at": {
        "type": "date"
      },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "popularity_score": {
        "type": "float"
      }
    }
  }
}
```

---

### 5. API网关服务 (API Gateway Service)

**职责**:
- 路由分发
- 认证授权
- 限流控制
- 日志记录

**技术栈**:
- FastAPI
- python-jose (JWT)
- fastapi-limiter

**API设计**:

```python
@app.get("/api/v1/contents")
async def get_contents(
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    获取内容列表

    Args:
        category: 分类过滤
        tags: 标签过滤
        page: 页码
        size: 每页数量

    Returns:
        内容列表
    """
    pass

@app.get("/api/v1/search")
async def search_contents(
    q: str,
    use_semantic: bool = False,
    page: int = 1,
    size: int = 20
):
    """
    搜索内容

    Args:
        q: 搜索查询
        use_semantic: 是否使用语义搜索
        page: 页码
        size: 每页数量

    Returns:
        搜索结果
    """
    pass
```

---

## 💾 数据层设计

### PostgreSQL设计

#### ER图

```
┌──────────────┐
│    users     │
├──────────────┤
│ id (PK)      │
│ email        │
│ preferences  │
│ created_at   │
└──────┬───────┘
       │
       │ 1:N
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌──────────────┐  ┌──────────────┐
│ user_actions │  │   api_keys   │
├──────────────┤  ├──────────────┤
│ id (PK)      │  │ id (PK)      │
│ user_id (FK) │  │ user_id (FK) │
│ content_id   │  │ key_hash     │
│ action_type  │  │ rate_limit   │
│ created_at   │  │ is_active    │
└──────────────┘  └──────────────┘

┌──────────────┐
│  contents    │
├──────────────┤
│ id (PK)      │
│ title        │
│ summary      │
│ original_url │
│ source       │
│ category     │
│ published_at │
│ embedding    │
│ metadata     │
│ created_at   │
└──────────────┘
```

### Redis设计

#### 数据结构

```
# 缓存
content:{id}                    # 内容详情缓存 (TTL: 1h)
user:{id}:recommendations       # 推荐结果缓存 (TTL: 15m)
search:{query_hash}:results     # 搜索结果缓存 (TTL: 5m)

# 排行榜
hot_contents:24h                # 24小时热门内容 (ZSET)
hot_contents:7d                 # 7天热门内容 (ZSET)

# 队列
queue:crawler:high              # 高优先级爬虫队列
queue:crawler:normal            # 普通优先级队列
queue:processing                # 处理队列

# 限流
ratelimit:{api_key}:{endpoint}  # 限流计数器
```

---

## 🚀 部署架构

### MVP阶段（单服务器）

```
┌─────────────────────────────────────────────┐
│     单台服务器 (4核8G内存)                    │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Nginx   │  │ Next.js  │  │ FastAPI  │ │
│  │  :80     │  │  :3000   │  │  :8000   │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │PostgreSQL│  │  Redis   │  │Elastic   │ │
│  │  :5432   │  │  :6379   │  │ :9200    │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌──────────┐  ┌──────────┐               │
│  │ Crawler  │  │Scheduler │               │
│  │ Service  │  │  (Cron)  │               │
│  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────┘
```

**成本**: $40-50/月

---

### 成长阶段（多服务器）

```
┌──────────────┐
│ 负载均衡器    │
│   (Nginx)    │
└──────┬───────┘
       │
       ├─────────────┬─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ App #1   │  │ App #2   │  │ App #3   │
│(FastAPI) │  │(FastAPI) │  │(FastAPI) │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌──────────────┐
│  PostgreSQL  │      │    Redis     │
│  (主从)       │      │  (集群)      │
└──────────────┘      └──────────────┘
```

**成本**: $150-300/月

---

## 📊 性能优化

### 缓存策略

1. **多级缓存**
   - L1: 应用内存 (LRU Cache)
   - L2: Redis (分布式缓存)
   - L3: CDN (Cloudflare)

2. **缓存失效**
   - TTL机制
   - 事件驱动（内容更新时）

### 数据库优化

1. **索引设计**
   - 基于高频查询模式
   - 使用复合索引

2. **查询优化**
   - 避免N+1问题
   - 延迟加载

3. **连接池**
   - SQLAlchemy Pool
   - PgBouncer

---

## 🔒 安全设计

### 认证授权

1. **JWT认证**
   - 访问令牌: 30分钟
   - 刷新令牌: 7天

2. **API Key认证**
   - 用户专属API密钥
   - 限流控制

### 数据保护

1. **加密**
   - 存储加密: PostgreSQL加密
   - 传输加密: TLS 1.3

2. **输入验证**
   - Pydantic验证
   - SQL注入防护

---

**最后更新**: 2024-03-26
**作者**: 系统架构师
