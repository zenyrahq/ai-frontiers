"""
Search API Routes with caching support
検索APIエンドポイント（キャッシュ対応）
"""
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
import hashlib

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "processing"))

from services.search_service import get_search_service
from services.cache_service import cache
from loguru import logger

# 埋め込みサービスの遅延インポート（processing ディレクトリから）
_embedding_service = None


def get_embedding_service():
    """埋め込みサービスを取得（遅延ロード）"""
    global _embedding_service
    if _embedding_service is None:
        from services.embedding_service import get_embedding_service as _get_service
        _embedding_service = _get_service()
    return _embedding_service


router = APIRouter(prefix="/api/v1/search", tags=["search"])


# リクエスト/レスポンスモデル
class SearchRequest(BaseModel):
    """検索リクエスト"""
    query: str = Field(..., min_length=1, max_length=500, description="検索クエリ")
    limit: int = Field(default=20, ge=1, le=100, description="最大結果数")
    vector_weight: float = Field(default=0.6, ge=0.0, le=1.0, description="ベクトル検索の重み")
    category: Optional[str] = Field(default=None, description="カテゴリフィルタ")
    source: Optional[str] = Field(default=None, description="ソースフィルタ")


class SearchResult(BaseModel):
    """検索結果"""
    id: int
    title: str
    summary: Optional[str]
    source: Optional[str]
    category: Optional[str]
    tags: Optional[List[str]]
    published_at: Optional[str]
    score: float = Field(..., description="関連度スコア")


class SearchResponse(BaseModel):
    """検索レスポンス"""
    query: str
    total: int
    results: List[SearchResult]
    search_type: str


class SuggestionResponse(BaseModel):
    """サジェストレスポンス"""
    query: str
    suggestions: List[str]


class RelatedContentResponse(BaseModel):
    """関連コンテンツレスポンス"""
    content_id: int
    related: List[SearchResult]


def _content_to_result(content, score: float) -> SearchResult:
    """Content オブジェクトを SearchResult に変換"""
    return SearchResult(
        id=content.id,
        title=content.title,
        summary=content.summary[:200] + "..." if content.summary and len(content.summary) > 200 else content.summary,
        source=content.source,
        category=content.category,
        tags=content.tags,
        published_at=content.published_at.isoformat() if content.published_at else None,
        score=round(score, 4)
    )


def _generate_search_cache_key(
    search_type: str,
    query: str,
    limit: int = 20,
    **kwargs
) -> str:
    """
    Generate cache key for search queries
    Uses hash for long queries to avoid key length issues
    """
    # Build key parts
    key_parts = [f"search:{search_type}"]

    # Hash the query for consistent key length
    query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
    key_parts.append(f"q:{query_hash}")
    key_parts.append(f"limit:{limit}")

    # Add other parameters
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")

    return ":".join(key_parts)


# Cache TTL constants (in seconds)
CACHE_TTL_SEARCH = 300        # 5 minutes for search results
CACHE_TTL_CATEGORY = 600      # 10 minutes for category browsing
CACHE_TTL_POPULAR = 900       # 15 minutes for popular content
CACHE_TTL_RELATED = 600       # 10 minutes for related content
CACHE_TTL_SUGGESTIONS = 300   # 5 minutes for suggestions


def _results_to_dict(results: List) -> List[dict]:
    """Convert search results to dict for caching"""
    return [
        {
            "id": content.id,
            "title": content.title,
            "summary": content.summary[:200] + "..." if content.summary and len(content.summary) > 200 else content.summary,
            "source": content.source,
            "category": content.category,
            "tags": content.tags,
            "published_at": content.published_at.isoformat() if content.published_at else None,
            "score": round(score, 4)
        }
        for content, score in results
    ]


def _dict_to_results(data: List[dict]) -> List[SearchResult]:
    """Convert cached dict back to SearchResult"""
    return [SearchResult(**item) for item in data]


def _contents_to_cache_dict(contents: List) -> List[dict]:
    """Convert Content objects to cacheable dict format"""
    return [
        {
            "id": c.id,
            "title": c.title,
            "summary": c.summary[:200] + "..." if c.summary and len(c.summary) > 200 else c.summary,
            "source": c.source,
            "category": c.category,
            "tags": c.tags,
            "published_at": c.published_at.isoformat() if c.published_at else None,
            "score": 1.0
        }
        for c in contents
    ]


@router.get("", response_model=SearchResponse)
async def hybrid_search(
    q: str = Query(..., min_length=1, max_length=500, description="検索クエリ"),
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数"),
    vector_weight: float = Query(default=0.6, ge=0.0, le=1.0, description="ベクトル検索の重み"),
    category: Optional[str] = Query(default=None, description="カテゴリフィルタ"),
    source: Optional[str] = Query(default=None, description="ソースフィルタ")
):
    """
    ハイブリッド検索（ベクトル + 全文検索）

    ベクトル検索と全文検索を組み合わせた高精度な検索を提供します。
    キャッシュ戦略：5分間キャッシュ

    - **q**: 検索クエリ文字列
    - **limit**: 返却する最大結果数（1-100）
    - **vector_weight**: ベクトル検索の重み（0.0-1.0、デフォルト0.6）
    - **category**: カテゴリでフィルタリング
    - **source**: ソースでフィルタリング
    """
    try:
        # Generate cache key
        cache_key = _generate_search_cache_key(
            "hybrid", q, limit,
            vector_weight=vector_weight,
            category=category,
            source=source
        )

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Hybrid search cache hit: '{q[:50]}'")
            return SearchResponse(
                query=q,
                total=cached["total"],
                results=_dict_to_results(cached["results"]),
                search_type="hybrid"
            )

        search_service = get_search_service()
        embedding_service = get_embedding_service()

        # クエリのベクトル埋め込みを生成
        query_embedding = embedding_service.generate_embedding(q)

        if not query_embedding:
            raise HTTPException(status_code=500, detail="埋め込み生成に失敗しました")

        # フィルタを構築
        filters = {}
        if category:
            filters["category"] = category
        if source:
            filters["source"] = source

        # ハイブリッド検索を実行
        results = await search_service.hybrid_search(
            query=q,
            query_embedding=query_embedding,
            limit=limit,
            vector_weight=vector_weight,
            filters=filters if filters else None
        )

        # 結果を変換
        search_results = [
            _content_to_result(content, score)
            for content, score in results
        ]

        # Cache the results (5 minutes)
        cache_data = {
            "total": len(search_results),
            "results": _results_to_dict(results)
        }
        await cache.set(cache_key, cache_data, ttl=300)

        logger.info(f"ハイブリッド検索: '{q[:50]}' -> {len(search_results)}件")

        return SearchResponse(
            query=q,
            total=len(search_results),
            results=search_results,
            search_type="hybrid"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ハイブリッド検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector", response_model=SearchResponse)
async def vector_search(
    q: str = Query(..., min_length=1, max_length=500, description="検索クエリ"),
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数"),
    threshold: float = Query(default=0.5, ge=0.0, le=1.0, description="最小類似度閾値"),
    category: Optional[str] = Query(default=None, description="カテゴリフィルタ"),
    source: Optional[str] = Query(default=None, description="ソースフィルタ")
):
    """
    ベクトル類似度検索

    意味的な類似性に基づく検索を提供します。

    - **q**: 検索クエリ文字列
    - **limit**: 返却する最大結果数
    - **threshold**: 最小類似度スコア（0.0-1.0）
    """
    try:
        search_service = get_search_service()
        embedding_service = get_embedding_service()

        # クエリのベクトル埋め込みを生成
        query_embedding = embedding_service.generate_embedding(q)

        if not query_embedding:
            raise HTTPException(status_code=500, detail="埋め込み生成に失敗しました")

        # フィルタを構築
        filters = {}
        if category:
            filters["category"] = category
        if source:
            filters["source"] = source

        # ベクトル検索を実行
        results = await search_service.vector_search(
            query_embedding=query_embedding,
            limit=limit,
            threshold=threshold,
            filters=filters if filters else None
        )

        # 結果を変換
        search_results = [
            _content_to_result(content, similarity)
            for content, similarity in results
        ]

        logger.info(f"ベクトル検索: '{q[:50]}' -> {len(search_results)}件")

        return SearchResponse(
            query=q,
            total=len(search_results),
            results=search_results,
            search_type="vector"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ベクトル検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fulltext", response_model=SearchResponse)
async def fulltext_search(
    q: str = Query(..., min_length=1, max_length=500, description="検索クエリ"),
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数"),
    category: Optional[str] = Query(default=None, description="カテゴリフィルタ"),
    source: Optional[str] = Query(default=None, description="ソースフィルタ")
):
    """
    全文検索

    PostgreSQLの全文検索機能を使用したキーワード検索を提供します。
    キャッシュ戦略：5分間キャッシュ

    - **q**: 検索クエリ文字列
    - **limit**: 返却する最大結果数
    """
    try:
        # Generate cache key
        cache_key = _generate_search_cache_key(
            "fulltext", q, limit, category=category, source=source
        )

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Full-text search cache hit: '{q[:50]}'")
            return SearchResponse(
                query=q,
                total=cached["total"],
                results=_dict_to_results(cached["results"]),
                search_type="fulltext"
            )

        search_service = get_search_service()

        # フィルタを構築
        filters = {}
        if category:
            filters["category"] = category
        if source:
            filters["source"] = source

        # 全文検索を実行
        results = await search_service.fulltext_search(
            query=q,
            limit=limit,
            filters=filters if filters else None
        )

        # 結果を変換
        search_results = [
            _content_to_result(content, rank)
            for content, rank in results
        ]

        # Cache the results (5 minutes)
        cache_data = {
            "total": len(search_results),
            "results": _results_to_dict(results)
        }
        await cache.set(cache_key, cache_data, ttl=CACHE_TTL_SEARCH)

        logger.info(f"全文検索: '{q[:50]}' -> {len(search_results)}件")

        return SearchResponse(
            query=q,
            total=len(search_results),
            results=search_results,
            search_type="fulltext"
        )

    except Exception as e:
        logger.error(f"全文検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="部分クエリ"),
    limit: int = Query(default=5, ge=1, le=20, description="最大サジェスト数")
):
    """
    検索サジェスト

    入力中のクエリに基づいて検索候補を提供します。
    キャッシュ戦略：5分間キャッシュ

    - **q**: 部分的な検索クエリ
    - **limit**: 返却する最大サジェスト数
    """
    try:
        # Generate cache key
        cache_key = f"search:suggestions:{hashlib.md5(q.encode()).hexdigest()[:16]}:{limit}"

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Suggestions cache hit: '{q}'")
            return SuggestionResponse(query=q, suggestions=cached["suggestions"])

        search_service = get_search_service()

        suggestions = await search_service.get_search_suggestions(
            query=q,
            limit=limit
        )

        # Cache the results (5 minutes)
        await cache.set(cache_key, {"suggestions": suggestions}, ttl=CACHE_TTL_SUGGESTIONS)

        logger.info(f"サジェスト: '{q}' -> {len(suggestions)}件")

        return SuggestionResponse(
            query=q,
            suggestions=suggestions
        )

    except Exception as e:
        logger.error(f"サジェストエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}", response_model=SearchResponse)
async def search_by_category(
    category: str,
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数"),
    offset: int = Query(default=0, ge=0, description="オフセット")
):
    """
    カテゴリ別検索

    指定されたカテゴリのコンテンツを取得します。
    キャッシュ戦略：10分間キャッシュ

    - **category**: カテゴリ名
    - **limit**: 返却する最大結果数
    - **offset**: ページネーション用オフセット
    """
    try:
        # Generate cache key
        cache_key = f"search:category:{category}:limit:{limit}:offset:{offset}"

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Category search cache hit: '{category}'")
            return SearchResponse(
                query=category,
                total=cached["total"],
                results=_dict_to_results(cached["results"]),
                search_type="category"
            )

        search_service = get_search_service()

        contents = await search_service.search_by_category(
            category=category,
            limit=limit,
            offset=offset
        )

        # 結果を変換（スコアは時系列順のため1.0）
        search_results = [
            _content_to_result(content, 1.0)
            for content in contents
        ]

        # Cache the results (10 minutes)
        cache_data = {
            "total": len(search_results),
            "results": [{"id": c.id, "title": c.title, "summary": c.summary[:200] + "..." if c.summary and len(c.summary) > 200 else c.summary, "source": c.source, "category": c.category, "tags": c.tags, "published_at": c.published_at.isoformat() if c.published_at else None, "score": 1.0} for c in contents]
        }
        await cache.set(cache_key, cache_data, ttl=CACHE_TTL_CATEGORY)

        logger.info(f"カテゴリ検索: '{category}' -> {len(search_results)}件")

        return SearchResponse(
            query=category,
            total=len(search_results),
            results=search_results,
            search_type="category"
        )

    except Exception as e:
        logger.error(f"カテゴリ検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags", response_model=SearchResponse)
async def search_by_tags(
    tags: str = Query(..., description="カンマ区切りのタグリスト"),
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数"),
    match_all: bool = Query(default=False, description="すべてのタグに一致")
):
    """
    タグ別検索

    指定されたタグを持つコンテンツを取得します。
    キャッシュ戦略：10分間キャッシュ

    - **tags**: カンマ区切りのタグリスト
    - **limit**: 返却する最大結果数
    - **match_all**: Trueの場合、すべてのタグに一致する必要があります
    """
    try:
        # タグをパース
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        if not tag_list:
            raise HTTPException(status_code=400, detail="タグを指定してください")

        # Generate cache key
        cache_key = f"search:tags:{hashlib.md5(','.join(sorted(tag_list)).encode()).hexdigest()[:16]}:limit:{limit}:all:{match_all}"

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Tags search cache hit: {tag_list}")
            return SearchResponse(
                query=", ".join(tag_list),
                total=cached["total"],
                results=_dict_to_results(cached["results"]),
                search_type="tags"
            )

        search_service = get_search_service()

        contents = await search_service.search_by_tags(
            tags=tag_list,
            limit=limit,
            match_all=match_all
        )

        # 結果を変換
        search_results = [
            _content_to_result(content, 1.0)
            for content in contents
        ]

        # Cache the results (10 minutes)
        cache_data = {
            "total": len(search_results),
            "results": _contents_to_cache_dict(contents)
        }
        await cache.set(cache_key, cache_data, ttl=CACHE_TTL_CATEGORY)

        logger.info(f"タグ検索: {tag_list} -> {len(search_results)}件")

        return SearchResponse(
            query=", ".join(tag_list),
            total=len(search_results),
            results=search_results,
            search_type="tags"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"タグ検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular", response_model=SearchResponse)
async def get_popular(
    days: int = Query(default=7, ge=1, le=30, description="過去何日分"),
    limit: int = Query(default=20, ge=1, le=100, description="最大結果数")
):
    """
    人気コンテンツ

    過去N日間の人気コンテンツを取得します。
    人気度 = 閲覧数 + いいね数 * 2
    キャッシュ戦略：15分間キャッシュ

    - **days**: 過去何日分を対象にするか
    - **limit**: 返却する最大結果数
    """
    try:
        # Generate cache key
        cache_key = f"search:popular:days:{days}:limit:{limit}"

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Popular search cache hit: {days} days")
            return SearchResponse(
                query=f"popular:{days}days",
                total=cached["total"],
                results=_dict_to_results(cached["results"]),
                search_type="popular"
            )

        search_service = get_search_service()

        contents = await search_service.get_popular_contents(
            days=days,
            limit=limit
        )

        # 結果を変換
        search_results = [
            _content_to_result(content, 1.0)
            for content in contents
        ]

        # Cache the results (15 minutes)
        cache_data = {
            "total": len(search_results),
            "results": _contents_to_cache_dict(contents)
        }
        await cache.set(cache_key, cache_data, ttl=CACHE_TTL_POPULAR)

        logger.info(f"人気コンテンツ: 過去{days}日 -> {len(search_results)}件")

        return SearchResponse(
            query=f"popular:{days}days",
            total=len(search_results),
            results=search_results,
            search_type="popular"
        )

    except Exception as e:
        logger.error(f"人気コンテンツ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/related/{content_id}", response_model=RelatedContentResponse)
async def get_related(
    content_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="最大結果数")
):
    """
    関連コンテンツ

    指定されたコンテンツに類似するコンテンツを取得します。
    キャッシュ戦略：10分間キャッシュ

    - **content_id**: コンテンツID
    - **limit**: 返却する最大結果数
    """
    try:
        # Generate cache key
        cache_key = f"search:related:content:{content_id}:limit:{limit}"

        # Try cache first
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info(f"Related search cache hit: content_id={content_id}")
            return RelatedContentResponse(
                content_id=content_id,
                related=_dict_to_results(cached["related"])
            )

        search_service = get_search_service()

        results = await search_service.get_related_contents(
            content_id=content_id,
            limit=limit
        )

        # 自分自身を除外
        related_results = [
            _content_to_result(content, similarity)
            for content, similarity in results
            if content.id != content_id
        ][:limit]

        # Cache the results (10 minutes)
        cache_data = {
            "related": _results_to_dict([(c, s) for c, s in results if c.id != content_id][:limit])
        }
        await cache.set(cache_key, cache_data, ttl=CACHE_TTL_RELATED)

        logger.info(f"関連コンテンツ: ID={content_id} -> {len(related_results)}件")

        return RelatedContentResponse(
            content_id=content_id,
            related=related_results
        )

    except Exception as e:
        logger.error(f"関連コンテンツ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))
