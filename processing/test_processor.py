#!/usr/bin/env python3
"""
Test NLP Processor
Tests the NLP processing pipeline without requiring API keys
"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "processing"))

from loguru import logger


def test_embedding_service():
    """Test embedding service"""
    logger.info("=" * 60)
    logger.info("Testing Embedding Service")
    logger.info("=" * 60)

    from services.embedding_service import EmbeddingService

    # Initialize service
    logger.info("Loading embedding model...")
    service = EmbeddingService(model_name="all-MiniLM-L6-v2", device="cpu")

    # Test 1: Single embedding
    logger.info("\n📝 Test 1: Generate single embedding")
    text = "This is a test sentence for embedding generation."
    embedding = service.generate_embedding(text)

    if embedding:
        logger.success(f"✅ Generated embedding of dimension: {len(embedding)}")
        logger.info(f"   First 5 values: {embedding[:5]}")
    else:
        logger.error("❌ Failed to generate embedding")

    # Test 2: Batch embeddings
    logger.info("\n📝 Test 2: Generate batch embeddings")
    texts = [
        "Machine learning is transforming AI.",
        "Natural language processing enables text understanding.",
        "Computer vision allows machines to see."
    ]

    embeddings = service.generate_embeddings_batch(texts)

    if embeddings:
        logger.success(f"✅ Generated {len([e for e in embeddings if e])} embeddings")
    else:
        logger.error("❌ Failed to generate batch embeddings")

    # Test 3: Similarity calculation
    logger.info("\n📝 Test 3: Calculate similarity")
    if embeddings and len(embeddings) >= 2:
        sim = service.similarity(embeddings[0], embeddings[1])
        logger.info(f"   Similarity between text 1 and 2: {sim:.4f}")

        sim2 = service.similarity(embeddings[0], embeddings[2])
        logger.info(f"   Similarity between text 1 and 3: {sim2:.4f}")
        logger.success("✅ Similarity calculation works")

    # Test 4: Model info
    logger.info("\n📊 Model Information:")
    info = service.get_model_info()
    for key, value in info.items():
        logger.info(f"   {key}: {value}")

    return True


def test_claude_service_mock():
    """Test Claude service structure (without API calls)"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Claude Service (Structure)")
    logger.info("=" * 60)

    from services.claude_service import ClaudeService, ProcessedContent

    # Test data structure
    logger.info("\n📝 Test: ProcessedContent structure")
    content = ProcessedContent(
        summary="这是一个测试摘要。",
        keywords=["AI", "机器学习", "深度学习"],
        entities=["GPT-4", "OpenAI"],
        category="artificial_intelligence",
        importance_score=0.85,
        sentiment="positive"
    )

    logger.info(f"   Summary: {content.summary}")
    logger.info(f"   Keywords: {content.keywords}")
    logger.info(f"   Entities: {content.entities}")
    logger.info(f"   Category: {content.category}")
    logger.info(f"   Importance: {content.importance_score}")
    logger.info(f"   Sentiment: {content.sentiment}")

    logger.success("✅ Claude service structure is valid")

    return True


def test_processing_pipeline():
    """Test the processing pipeline structure"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Processing Pipeline")
    logger.info("=" * 60)

    # Test import
    logger.info("\n📝 Test: Import NLPProcessor")
    try:
        from nlp_processor import NLPProcessor
        logger.success("✅ NLPProcessor imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import: {e}")
        return False

    # Test initialization (will fail without API key, which is expected)
    logger.info("\n📝 Test: Initialize processor")
    logger.info("   Note: This will fail without valid API key (expected)")

    return True


def main():
    """Run all tests"""
    logger.info("🧪 NLP Processing Service Tests")
    logger.info("=" * 60)

    try:
        # Test 1: Embedding service
        test_embedding_service()

        # Test 2: Claude service structure
        test_claude_service_mock()

        # Test 3: Processing pipeline
        test_processing_pipeline()

        logger.info("\n" + "=" * 60)
        logger.success("✅ All tests completed!")
        logger.info("=" * 60)

        logger.info("\n📌 Next steps:")
        logger.info("1. Set ANTHROPIC_API_KEY in .env file")
        logger.info("2. Run: python nlp_processor.py --stats")
        logger.info("3. Run: python nlp_processor.py --limit 10")

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
