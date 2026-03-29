#!/usr/bin/env python3
"""
Full System Test Script
完整系统测试脚本
"""
import sys
import asyncio
from pathlib import Path

# Add paths
api_dir = Path(__file__).parent.parent / "api"
processing_dir = Path(__file__).parent.parent / "processing"
sys.path.insert(0, str(api_dir))
sys.path.insert(0, str(processing_dir))

from loguru import logger
from sqlalchemy import text
from core.database import AsyncSessionLocal
from models.models import Content
from services.embedding_service import get_embedding_service


# Sample test data
TEST_CONTENTS = [
    {
        "title": "Attention Is All You Need",
        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "source": "arxiv",
        "category": "deep_learning",
        "tags": ["transformer", "attention", "nlp"],
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "summary": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["bert", "transformer", "pre-training"],
    },
    {
        "title": "GPT-4 Technical Report",
        "summary": "We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs and produce text outputs. While less capable than humans in many real-world scenarios, GPT-4 exhibits human-level performance on various professional and academic benchmarks.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["gpt", "llm", "multimodal"],
    },
    {
        "title": "Deep Residual Learning for Image Recognition",
        "summary": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.",
        "source": "arxiv",
        "category": "computer_vision",
        "tags": ["resnet", "deep-learning", "image-recognition"],
    },
    {
        "title": "Generative Adversarial Networks",
        "summary": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["gan", "generative", "adversarial"],
    },
    {
        "title": "Adam: A Method for Stochastic Optimization",
        "summary": "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments. The method is straightforward to implement, computationally efficient, has little memory requirements, and is well suited for problems that are large in terms of data and/or parameters.",
        "source": "arxiv",
        "category": "machine_learning",
        "tags": ["optimization", "adam", "gradient-descent"],
    },
]


async def insert_test_data():
    """Insert test data into database"""
    logger.info("=" * 60)
    logger.info("插入测试数据")
    logger.info("=" * 60)

    embedding_service = get_embedding_service()

    async with AsyncSessionLocal() as session:
        # Check existing data
        result = await session.execute(text("SELECT COUNT(*) FROM contents"))
        existing_count = result.scalar()

        if existing_count > 0:
            logger.info(f"数据库已有 {existing_count} 条数据，跳过插入")
            return existing_count

        # Insert test data
        inserted = 0
        for item in TEST_CONTENTS:
            # Generate embedding
            text_for_embedding = f"{item['title']} {item['summary']}"
            embedding = embedding_service.generate_embedding(text_for_embedding)

            # Create content
            content = Content(
                title=item["title"],
                summary=item["summary"],
                content=item["summary"],
                source=item["source"],
                category=item["category"],
                tags=item["tags"],
                original_url=f"https://arxiv.org/abs/test-{inserted + 1}",
                embedding=embedding,
                is_processed=True,
                view_count=100 - inserted * 10,
                like_count=50 - inserted * 5,
            )
            session.add(content)
            inserted += 1
            logger.info(f"  插入: {item['title'][:50]}...")

        await session.commit()
        logger.success(f"✅ 成功插入 {inserted} 条测试数据")

        return inserted


async def test_search():
    """Test search functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("测试搜索功能")
    logger.info("=" * 60)

    # Import search service
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "search_service",
        api_dir / "services" / "search_service.py"
    )
    search_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_module)
    search_service = search_module.get_search_service()

    embedding_service = get_embedding_service()

    # Test 1: Vector search
    logger.info("\n📝 测试1: 向量搜索")
    query = "transformer architecture"
    query_embedding = embedding_service.generate_embedding(query)
    results = await search_service.vector_search(query_embedding, limit=3)
    logger.info(f"   查询: '{query}'")
    logger.info(f"   结果: {len(results)} 条")
    for content, score in results[:2]:
        logger.info(f"   - [{score:.4f}] {content.title[:40]}...")

    # Test 2: Fulltext search
    logger.info("\n📝 测试2: 全文搜索")
    query = "neural network"
    results = await search_service.fulltext_search(query, limit=3)
    logger.info(f"   查询: '{query}'")
    logger.info(f"   结果: {len(results)} 条")
    for content, rank in results[:2]:
        logger.info(f"   - [{rank:.4f}] {content.title[:40]}...")

    # Test 3: Hybrid search
    logger.info("\n📝 测试3: 混合搜索")
    query = "language model"
    query_embedding = embedding_service.generate_embedding(query)
    results = await search_service.hybrid_search(query, query_embedding, limit=3)
    logger.info(f"   查询: '{query}'")
    logger.info(f"   结果: {len(results)} 条")
    for content, score in results[:2]:
        logger.info(f"   - [{score:.4f}] {content.title[:40]}...")

    # Test 4: Category search
    logger.info("\n📝 测试4: 分类搜索")
    results = await search_service.search_by_category("generative_ai", limit=3)
    logger.info(f"   分类: generative_ai")
    logger.info(f"   结果: {len(results)} 条")
    for content in results[:2]:
        logger.info(f"   - {content.title[:40]}...")

    # Test 5: Popular contents
    logger.info("\n📝 测试5: 热门内容")
    results = await search_service.get_popular_contents(days=30, limit=3)
    logger.info(f"   结果: {len(results)} 条")
    for content in results[:2]:
        logger.info(f"   - {content.title[:40]}... (views: {content.view_count})")

    # Test 6: Suggestions
    logger.info("\n📝 测试6: 搜索建议")
    suggestions = await search_service.get_search_suggestions("Trans", limit=5)
    logger.info(f"   查询: 'Trans'")
    logger.info(f"   建议: {suggestions}")

    return True


async def test_api_endpoints():
    """Test API endpoints via HTTP"""
    import aiohttp

    logger.info("\n" + "=" * 60)
    logger.info("测试 API 端点")
    logger.info("=" * 60)

    base_url = "http://localhost:8000"

    async with aiohttp.ClientSession() as client:
        # Test health
        logger.info("\n📝 测试: /health")
        async with client.get(f"{base_url}/health") as resp:
            data = await resp.json()
            logger.info(f"   状态: {data['status']}")

        # Test search
        logger.info("\n📝 测试: /api/v1/search")
        async with client.get(f"{base_url}/api/v1/search", params={"q": "transformer", "limit": 3}) as resp:
            data = await resp.json()
            logger.info(f"   查询: {data['query']}")
            logger.info(f"   结果数: {data['total']}")
            for item in data['results'][:2]:
                logger.info(f"   - [{item['score']:.4f}] {item['title'][:40]}...")

        # Test suggestions
        logger.info("\n📝 测试: /api/v1/search/suggestions")
        async with client.get(f"{base_url}/api/v1/search/suggestions", params={"q": "Deep", "limit": 3}) as resp:
            data = await resp.json()
            logger.info(f"   建议: {data['suggestions']}")

        # Test popular
        logger.info("\n📝 测试: /api/v1/search/popular")
        async with client.get(f"{base_url}/api/v1/search/popular", params={"days": 30, "limit": 3}) as resp:
            data = await resp.json()
            logger.info(f"   结果数: {data['total']}")

    return True


async def main():
    """Main test flow"""
    logger.info("🧪 AI Frontiers 完整系统测试")
    logger.info("=" * 60)

    # Step 1: Insert test data
    await insert_test_data()

    # Step 2: Test search functionality
    await test_search()

    # Step 3: Test API endpoints
    try:
        await test_api_endpoints()
    except Exception as e:
        logger.warning(f"API 端点测试跳过（可能需要启动后端服务）: {e}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("测试完成！")
    logger.info("=" * 60)
    logger.info("\n📌 下一步:")
    logger.info("1. 前端访问: cd frontend && npm run dev")
    logger.info("2. 浏览器打开: http://localhost:3000")
    logger.info("3. 测试搜索功能")


if __name__ == "__main__":
    asyncio.run(main())
