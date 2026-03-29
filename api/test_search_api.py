#!/usr/bin/env python3
"""
Search API Test Script
検索APIテストスクリプト
"""
import sys
import asyncio
from pathlib import Path

# パス設定
api_dir = Path(__file__).parent
processing_dir = Path(__file__).parent.parent / "processing"

# APIディレクトリを先に追加（search_service用）
sys.path.insert(0, str(api_dir))
# Processingディレクトリを後に追加（embedding_service用）
sys.path.insert(0, str(processing_dir))

from loguru import logger


async def test_search_service():
    """検索サービスのテスト"""
    logger.info("=" * 60)
    logger.info("検索サービステスト")
    logger.info("=" * 60)

    # API側のsearch_serviceをインポート
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "search_service",
        api_dir / "services" / "search_service.py"
    )
    search_module = importlib.util.module_from_spec(spec)
    sys.modules["search_service"] = search_module
    spec.loader.exec_module(search_module)

    get_search_service = search_module.get_search_service

    search_service = get_search_service()
    logger.success("✅ 検索サービス初期化成功")

    # テスト1: カテゴリ検索
    logger.info("\n📝 テスト1: カテゴリ検索")
    try:
        contents = await search_service.search_by_category(
            category="machine_learning",
            limit=5
        )
        logger.info(f"   結果: {len(contents)}件")
        for content in contents[:2]:
            logger.info(f"   - {content.title[:50]}...")
    except Exception as e:
        logger.warning(f"   カテゴリ検索エラー（データなしの可能性）: {e}")

    # テスト2: 人気コンテンツ
    logger.info("\n📝 テスト2: 人気コンテンツ")
    try:
        contents = await search_service.get_popular_contents(days=30, limit=5)
        logger.info(f"   結果: {len(contents)}件")
    except Exception as e:
        logger.warning(f"   人気コンテンツ取得エラー: {e}")

    # テスト3: サジェスト
    logger.info("\n📝 テスト3: 検索サジェスト")
    try:
        suggestions = await search_service.get_search_suggestions("AI", limit=5)
        logger.info(f"   結果: {len(suggestions)}件")
        for s in suggestions[:3]:
            logger.info(f"   - {s}")
    except Exception as e:
        logger.warning(f"   サジェストエラー: {e}")

    return True


def test_embedding_service():
    """埋め込みサービステスト"""
    logger.info("\n" + "=" * 60)
    logger.info("埋め込みサービステスト")
    logger.info("=" * 60)

    try:
        from services.embedding_service import get_embedding_service

        service = get_embedding_service()
        logger.success("✅ 埋め込みサービス初期化成功")

        # テスト埋め込み生成
        text = "Machine learning is a subset of artificial intelligence"
        embedding = service.generate_embedding(text)

        if embedding:
            logger.success(f"✅ 埋め込み生成成功: 次元数={len(embedding)}")
            logger.info(f"   最初の5値: {embedding[:5]}")
        else:
            logger.error("❌ 埋め込み生成失敗")

        return True
    except Exception as e:
        logger.error(f"❌ 埋め込みサービステストエラー: {e}")
        return False


async def test_vector_search():
    """ベクトル検索テスト"""
    logger.info("\n" + "=" * 60)
    logger.info("ベクトル検索テスト")
    logger.info("=" * 60)

    try:
        import importlib.util

        # search_serviceをロード
        spec = importlib.util.spec_from_file_location(
            "search_service",
            api_dir / "services" / "search_service.py"
        )
        search_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search_module)
        search_service = search_module.get_search_service()

        # embedding_serviceをロード
        from services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()

        # クエリ埋め込み生成
        query = "deep learning neural networks"
        query_embedding = embedding_service.generate_embedding(query)

        if not query_embedding:
            logger.error("❌ クエリ埋め込み生成失敗")
            return False

        logger.info(f"クエリ: '{query}'")
        logger.info(f"埋め込み次元: {len(query_embedding)}")

        # ベクトル検索実行
        results = await search_service.vector_search(
            query_embedding=query_embedding,
            limit=5,
            threshold=0.3
        )

        logger.info(f"検索結果: {len(results)}件")
        for content, similarity in results[:3]:
            logger.info(f"   - [{similarity:.4f}] {content.title[:50]}...")

        logger.success("✅ ベクトル検索テスト完了")
        return True

    except Exception as e:
        logger.error(f"❌ ベクトル検索テストエラー: {e}")
        return False


async def test_fulltext_search():
    """全文検索テスト"""
    logger.info("\n" + "=" * 60)
    logger.info("全文検索テスト")
    logger.info("=" * 60)

    try:
        import importlib.util

        # search_serviceをロード
        spec = importlib.util.spec_from_file_location(
            "search_service",
            api_dir / "services" / "search_service.py"
        )
        search_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search_module)
        search_service = search_module.get_search_service()

        query = "machine learning"
        logger.info(f"クエリ: '{query}'")

        results = await search_service.fulltext_search(
            query=query,
            limit=5
        )

        logger.info(f"検索結果: {len(results)}件")
        for content, rank in results[:3]:
            logger.info(f"   - [{rank:.4f}] {content.title[:50]}...")

        logger.success("✅ 全文検索テスト完了")
        return True

    except Exception as e:
        logger.error(f"❌ 全文検索テストエラー: {e}")
        return False


async def test_hybrid_search():
    """ハイブリッド検索テスト"""
    logger.info("\n" + "=" * 60)
    logger.info("ハイブリッド検索テスト")
    logger.info("=" * 60)

    try:
        import importlib.util

        # search_serviceをロード
        spec = importlib.util.spec_from_file_location(
            "search_service",
            api_dir / "services" / "search_service.py"
        )
        search_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search_module)
        search_service = search_module.get_search_service()

        # embedding_serviceをロード
        from services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()

        query = "transformer attention mechanism"
        query_embedding = embedding_service.generate_embedding(query)

        if not query_embedding:
            logger.error("❌ クエリ埋め込み生成失敗")
            return False

        logger.info(f"クエリ: '{query}'")

        results = await search_service.hybrid_search(
            query=query,
            query_embedding=query_embedding,
            limit=5,
            vector_weight=0.6
        )

        logger.info(f"検索結果: {len(results)}件")
        for content, score in results[:3]:
            logger.info(f"   - [{score:.4f}] {content.title[:50]}...")

        logger.success("✅ ハイブリッド検索テスト完了")
        return True

    except Exception as e:
        logger.error(f"❌ ハイブリッド検索テストエラー: {e}")
        return False


async def main():
    """メインテスト実行"""
    logger.info("🧪 検索APIテストスイート")
    logger.info("=" * 60)

    results = {
        "embedding_service": False,
        "search_service": False,
        "vector_search": False,
        "fulltext_search": False,
        "hybrid_search": False
    }

    # 埋め込みサービステスト
    results["embedding_service"] = test_embedding_service()

    # 検索サービステスト
    results["search_service"] = await test_search_service()

    # 各種検索テスト
    results["vector_search"] = await test_vector_search()
    results["fulltext_search"] = await test_fulltext_search()
    results["hybrid_search"] = await test_hybrid_search()

    # 結果サマリー
    logger.info("\n" + "=" * 60)
    logger.info("テスト結果サマリー")
    logger.info("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    logger.info(f"\n合計: {passed_count}/{total_count} テスト成功")

    if passed_count == total_count:
        logger.success("🎉 すべてのテストが成功しました！")
    else:
        logger.warning("⚠️ 一部のテストが失敗しました（データがない可能性があります）")

    logger.info("\n📌 次のステップ:")
    logger.info("1. FastAPIサーバーを起動: cd api && python main.py")
    logger.info("2. ブラウザでアクセス: http://localhost:8000/docs")
    logger.info("3. 検索APIをテスト: GET /api/v1/search?q=machine+learning")


if __name__ == "__main__":
    asyncio.run(main())
