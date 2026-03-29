# API设计文档

## 📝 概述

AI Frontiers API基于RESTful架构设计。

**基础URL**: `https://api.aifrontiers.com/v1`

**认证方式**: Bearer Token (JWT) 或 API Key

---

## 🔐 认证

### JWT认证

```http
Authorization: Bearer <access_token>
```

### API Key认证

```http
X-API-Key: <your_api_key>
```

---

## 📚 端点列表

### 1. 认证相关

#### 1.1 用户注册

```http
POST /auth/register
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "preferences": {
    "language": "zh",
    "categories": ["nlp", "computer_vision"]
  }
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-03-15T10:30:00Z"
}
```

---

#### 1.2 登录

```http
POST /auth/login
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**响应** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 2. 内容相关

#### 2.1 获取内容列表

```http
GET /contents?page=1&size=20&category=nlp&tags=transformer&sort=published_at
```

**参数**:
- `page` (int): 页码 (默认: 1)
- `size` (int): 每页数量 (默认: 20, 最大: 100)
- `category` (string, 可选): 分类过滤
- `tags` (string, 可选): 标签过滤（逗号分隔）
- `sort` (string, 可选): 排序方式 (published_at, popularity)
- `language` (string, 可选): 语言 (zh, en)

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 123,
      "title": "GPT-4新功能介绍",
      "summary": "GPT-4新增功能的详细说明...",
      "category": "nlp",
      "tags": ["gpt-4", "openai", "llm"],
      "source": "OpenAI Blog",
      "original_url": "https://openai.com/blog/...",
      "published_at": "2024-03-15T09:00:00Z",
      "view_count": 1234,
      "like_count": 56
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

#### 2.2 获取内容详情

```http
GET /contents/{content_id}
```

**响应** (200 OK):
```json
{
  "id": 123,
  "title": "GPT-4新功能介绍",
  "summary": "GPT-4新增功能的详细说明...",
  "content": "全文内容...",
  "category": "nlp",
  "tags": ["gpt-4", "openai", "llm"],
  "source": "OpenAI Blog",
  "original_url": "https://openai.com/blog/...",
  "published_at": "2024-03-15T09:00:00Z",
  "translations": {
    "en": "Introduction to new features of GPT-4...",
    "ja": "GPT-4の新機能について..."
  },
  "related_contents": [
    {
      "id": 124,
      "title": "相关文章1",
      "similarity_score": 0.85
    }
  ],
  "metadata": {
    "author": "OpenAI Team",
    "read_time": 5
  }
}
```

---

#### 2.3 搜索

```http
GET /search?q=gpt-4&use_semantic=true&page=1&size=20
```

**参数**:
- `q` (string): 搜索查询
- `use_semantic` (bool): 使用语义搜索 (默认: false)
- `page` (int): 页码
- `size` (int): 每页数量
- `filters` (object, 可选): 过滤条件

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 123,
      "title": "GPT-4新功能介绍",
      "summary": "...",
      "highlight": "GPT-4<em>新增</em>功能...",
      "score": 0.92
    }
  ],
  "total": 45,
  "page": 1,
  "size": 20,
  "query_time_ms": 45
}
```

---

### 3. 推荐相关

#### 3.1 个性化推荐

```http
GET /recommendations?page=1&size=20
```

**请求头**: `Authorization: Bearer <token>`

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 125,
      "title": "Claude 3最新信息",
      "summary": "...",
      "recommendation_reason": "与您浏览的文章相关",
      "score": 0.88
    }
  ],
  "algorithm": "hybrid",
  "last_updated": "2024-03-15T10:00:00Z"
}
```

---

#### 3.2 相似内容推荐

```http
GET /contents/{content_id}/similar?k=10
```

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 126,
      "title": "相似文章1",
      "similarity_score": 0.91
    }
  ],
  "based_on": {
    "id": 123,
    "title": "原文章"
  }
}
```

---

### 4. 用户相关

#### 4.1 获取用户信息

```http
GET /users/me
```

**请求头**: `Authorization: Bearer <token>`

**响应** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "preferences": {
    "language": "zh",
    "categories": ["nlp", "computer_vision"],
    "daily_digest": true
  },
  "stats": {
    "views_count": 234,
    "likes_count": 45,
    "bookmarks_count": 12
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### 4.2 更新用户设置

```http
PATCH /users/me
```

**请求体**:
```json
{
  "preferences": {
    "language": "en",
    "categories": ["nlp", "reinforcement_learning"]
  }
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "preferences": {
    "language": "en",
    "categories": ["nlp", "reinforcement_learning"]
  }
}
```

---

#### 4.3 记录用户行为

```http
POST /users/me/actions
```

**请求体**:
```json
{
  "content_id": 123,
  "action_type": "view"  // view, like, bookmark, share
}
```

**响应** (201 Created):
```json
{
  "success": true,
  "action_id": 5678
}
```

---

### 5. API Key管理

#### 5.1 创建API Key

```http
POST /api-keys
```

**请求体**:
```json
{
  "name": "我的应用",
  "rate_limit": 100
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "我的应用",
  "api_key": "ak_live_abc123...",  // 仅首次显示
  "rate_limit": 100,
  "created_at": "2024-03-15T10:00:00Z"
}
```

---

#### 5.2 API Key列表

```http
GET /api-keys
```

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "name": "我的应用",
      "key_prefix": "ak_live_abc***",
      "rate_limit": 100,
      "last_used_at": "2024-03-15T09:30:00Z",
      "created_at": "2024-03-15T10:00:00Z"
    }
  ]
}
```

---

### 6. 知识图谱

#### 6.1 获取实体关系

```http
GET /knowledge-graph/{entity}?depth=2
```

**参数**:
- `entity` (string): 实体名（例: "GPT-4"）
- `depth` (int): 关系深度 (默认: 2, 最大: 3)

**响应** (200 OK):
```json
{
  "nodes": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "type": "model",
      "description": "OpenAI开发的大语言模型"
    },
    {
      "id": "openai",
      "name": "OpenAI",
      "type": "company"
    }
  ],
  "edges": [
    {
      "source": "gpt-4",
      "target": "openai",
      "relation": "developed_by",
      "weight": 0.95
    }
  ]
}
```

---

## 🚦 限流

### 限制

| 方案 | 请求数 | 时间段 |
|------|--------|--------|
| 免费 | 100 | 1小时 |
| Basic | 1,000 | 1小时 |
| Pro | 10,000 | 1小时 |

### 响应头

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

---

## ❌ 错误响应

### 错误格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入参数无效",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

### HTTP状态码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 超过限流
- `500 Internal Server Error`: 服务器错误

---

## 📊 统计信息API

#### 站点统计

```http
GET /stats
```

**响应** (200 OK):
```json
{
  "total_contents": 5000,
  "total_users": 1200,
  "active_users_today": 234,
  "popular_categories": [
    {"name": "nlp", "count": 1500},
    {"name": "computer_vision", "count": 1200}
  ],
  "last_updated": "2024-03-15T10:00:00Z"
}
```

---

## 🔄 Webhooks

### 事件订阅

```http
POST /webhooks
```

**请求体**:
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["content.created", "content.updated"],
  "secret": "webhook_secret"
}
```

**事件载荷**:
```json
{
  "event": "content.created",
  "timestamp": "2024-03-15T10:00:00Z",
  "data": {
    "id": 123,
    "title": "新文章",
    "url": "https://aifrontiers.com/contents/123"
  }
}
```

---

## 📖 SDK

### Python SDK

```python
from ai_frontiers import Client

client = Client(api_key="your_api_key")

# 获取内容列表
contents = client.contents.list(
    category="nlp",
    page=1,
    size=20
)

# 搜索
results = client.search(
    q="GPT-4",
    use_semantic=True
)

# 获取推荐
recommendations = client.recommendations.get()
```

---

**最后更新**: 2024-03-26
**API版本**: v1
